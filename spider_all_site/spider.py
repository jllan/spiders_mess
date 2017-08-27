# coding: utf-8

import requests
import codecs
import json
import os
import re
from requests.adapters import HTTPAdapter
from requests.packages.urllib3 import Retry
from lxml import etree
from readability import Document
from newspaper import Article
from tld import get_tld
from urllib import parse
from model import Item, Session, init_db
from config import TARGET_DIR, HOST, logger


class Spider:
    def __init__(self, root_url):
        self.root_url = root_url
        self.domain = get_tld(root_url)

        self.links_await = set()  # 带爬取的url
        self.links_visited = set() # 已爬取的url
        self.attachment_saved = set() # 已保存的附件url
        self.links_all_dict = {} # 以字典形式保存所有的链接{url: title}，不含附件

        self.s = requests.Session()
        retries = Retry(total=3,
                        backoff_factor=0.1,
                        status_forcelist=[404, 500, 502, 503, 504])
        self.s.mount('http://', HTTPAdapter(max_retries=retries))

        # 初始化数据库和附件保存目录
        init_db()
        self.target_dir = os.path.join(TARGET_DIR, self.domain)
        if not os.path.exists(self.target_dir):
            os.mkdir(self.target_dir)

    def request(self, url, stream=False):
        '''网络请求，错误页面直接丢失'''
        logger.info('请求链接 {}'.format(url))
        headers = {'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux i686; rv:54.0) Gecko/20100101 Firefox/54.0'}
        try:
            web = self.s.get(url, headers=headers, timeout=60, stream=stream)
            if not web.ok:
                raise Exception
        except Exception as e:
            logger.warning('{} 请求出错，错误原因 {}，已放弃该页面'.format(url, e))
            web = None
        return web

    def parse(self, url):
        web = self.request(url)
        if web:
            item = {}
            item['link'] = url
            links_dict, attachment_dict, structure = self.parse_links(url, web.text)
            title, text = self.parse_text(url, web.text)  # 核心文本内容
            # structure = self.parse_structure(web.text)
            item['structure'] = structure
            item['title'] = title
            item['text'] = text
            if links_dict:
                self.save_links(links_dict)
            if attachment_dict:
                item['attachment'] = json.dumps(attachment_dict)
                print(item)
                self.save_attachment(attachment_dict)
            self.save_item(item)

    def parse_links(self, url, doc):
        '''解析出当前页面下属于本域名下的所有链接、附件等'''
        try:
            doc = etree.HTML(doc)
            a_tags = doc.xpath('//a[@href]')
            if not a_tags:
                raise Exception
        except Exception as e:
            logger.warning('{} 解析出错，错误原因 {}'.format(url, e))
            return [None]*3

        # 查找当前页面所在整个网站的位置，即导航
        structure = doc.xpath('//*[contains(text(), "位置")]/*/text()') # 含有‘位置’字样的标签下的所有子标签的文本
        # structure = selector.xpath('//*[ends-with(text(), "位置")]/*/text()').extract()
        if not structure:
            structure = doc.xpath('//*[contains(text(), "位置")]/following-sibling::*/text()') # 含有‘位置’字样的标签之后同级别的所有标签的文本
        structure = [re.sub('\W+', '', s).strip() for s in structure]
        structure = list(filter(lambda s: s and s.strip(), structure))
        structure = '-'.join(structure)

        # 解析链接
        links_dict = {} # 当前页面的所有链接{url1: title2, url2: title2, ...}
        attachments_dict = {} # 当前页面的所有附件{url1: title2, url2: title2, ...}
        for tag in a_tags:
            link = tag.xpath('@href')[0]
            if not str.startswith(link, '#'):
                link = parse.urljoin(self.root_url, link)
                try:
                    assert get_tld(link) == self.domain # 只要本域下的链接
                except Exception as e:
                    continue
                else:
                    logger.info('解析 {}找到链接 {}'.format(url, link))

                    try:
                        link_title = tag.xpath('@title')[0].strip() # 找a标签内的title
                        if not link_title:
                            link_title = ''.join(tag.xpath('.//text()'))
                            if not link_title:
                                raise Exception
                    except Exception as e:
                        logger.warning('没有找到链接 {} 的title，原因 {}'.format(link, e))
                        link_title = self.links_all_dict.get(url, link) # 如果找不到链接的title，就把title设为该链接当前页面网址的title
                    else:
                        logger.info('找到链接 {} 的title {}'.format(link, link_title))
                    link_title = link_title.replace('/', '-') # 如果title中有‘/’将无法创建一个以该title为名字的文件

                    link_type = link.split('.')[-1].strip().lower()
                    # 如果链接是个附件，则保存附件相关信息
                    if link_type in \
                            ['doc', 'docx', 'ppt', 'pptx', 'pdf', 'xls', 'xlsx', 'txt', 'zip', 'rar', 'png', 'jpg']:
                        logger.info('解析 {} 找到附件 {}'.format(url, link))
                        attachments_dict[link] = link_title
                    else:
                        # 如果链接不是附件，则把链接加入待抓取队列，而且只要www的链接
                        if parse.urlparse(link).netloc in [self.domain, 'www.' + self.domain] and link not in links_dict.keys():
                            links_dict[link] = link_title
        return links_dict, attachments_dict, structure

    def parse_text2(self, url, doc):
        '''解析网页中的文本数据：正文，标题，发布时间，作者等'''
        article = Document(doc)
        try:
            text = article.summary()
            # 如果找不到当前页面的title，就把title设为当前页面的链接的title
            title = article.title() if article.title() else self.links_all_dict.get(url, '')
        except Exception as e:
            logger.warning('没有找到页面 {} 的title和text，原因 {}'.format(url, e))
            title, text = '', ''
        return title, text

    def parse_text(self, url, doc):
        '''解析网页中的文本数据：正文，标题，发布时间，作者等'''
        article = Article(url, language='zh')
        try:
            article.download()
            article.parse()
            # 如果找不到当前页面的title，就把title设为当前页面的链接的title
        except Exception as e:
            logger.warning('没有找到页面 {} 的title和text，原因 {}'.format(url, e))
            title, text = '', ''
        else:
            title = article.title if article.title else self.links_all_dict.get(url, '')
            text = article.text
        return title, text

    def parse_table(self):
        '''解析网页中表格数据'''
        pass

    def save_links(self, links_dict):
        for link, title in links_dict.items():
            if link not in self.links_visited:
                self.links_await.add(link)
                self.links_all_dict[link] = title
                self.write(link)

    def save_attachment(self, attachment_dict):
        '''保存附件，附件名是附件链接的标题名'''
        for link, title in attachment_dict.items():
            if link not in self.attachment_saved: # 之前没有保存过该附件
                filename = title
                file_type = link.split('.')[-1]
                if title.split('.')[-1] != file_type:
                    filename = title+'.'+file_type
                r = self.request(link, stream=True)
                if r:
                    attachment_name = os.path.join(self.target_dir, filename)
                    with open(attachment_name, 'wb') as f:
                        for chunk in r.iter_content(chunk_size=1024):
                            f.write(chunk)
                    self.attachment_saved.add(link)
                    logger.info('附件 {} 已保存'.format(link))
                else:
                    logger.warning('附件 {} 保存失败'.format(link))
            else:
                logger.info('附件 {} 已存在'.format(link))

    def save_item(self, item):
        '''写数据库'''
        session = Session()
        try:
            session.add(Item(**item))
            session.commit()
        except Exception as e:
            logger.warning('页面 {} 的数据写入数据库出错，错误原因{}'.format(item['link'], e))
            session.rollback()
        session.close()

    def write(self, link):
        with codecs.open(os.path.join(self.target_dir, 'sites.txt'), 'a+', 'utf8') as f1:
            f1.write(link+'\n')

        with codecs.open(os.path.join(self.target_dir, 'sites_unique.txt'), 'a+', 'utf8') as f2:
            if link not in [line.strip() for line in f2.readlines()]:
                f2.write(link+'\n')

    def main(self):
        self.links_await.add(self.root_url)
        while self.links_await:
            link = self.links_await.pop()
            logger.info('获取链接 {}，目前剩余链接数目 {}'.format(link, len(self.links_await)))
            if link not in self.links_visited:
                self.links_visited.add(link)
                self.parse(link)


if __name__ == '__main__':
    root_url = HOST
    spider = Spider(root_url)
    spider.main()
