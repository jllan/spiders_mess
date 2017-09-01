from urllib import parse
import json
import os
import codecs
import time
import re
import requests
from readability import Document
from newspaper import Article
from scrapy.http import Request
from scrapy.selector import Selector
from scrapy.spiders import CrawlSpider
from tld import get_tld

from SpiderWholeSite.items import SpiderwholesiteItem, AttachmentItem
from config import HOST, DOMAIN


class Spider(CrawlSpider):
    name = "WholeSiteSpider"
    host = HOST
    domain = get_tld(host)
    # allowed_domains = DOMAIN
    start_urls = HOST
    attachment_link = set()

    def start_requests(self):
        yield Request(url=self.start_urls, meta={'link_title': ''}, callback=self.parse_item)  # 去解析链接

    def parse_item(self, response):
        print('解析链接 ', response.url)
        '''解析出属于本域名下的所有链接和附件'''
        item = SpiderwholesiteItem()
        item['link'] = response.url

        # # 使用newspaper解析
        # article = Article(response.url, language='zh')
        # try:
        #     article.download()
        #     article.parse()
        # except Exception as e:
        #     title, text = '', ''
        # else:
        #     title = article.title
        #     text = article.text
        # item['title'] = title if title else response.meta['link_title'] # 如果找不到当前页面的title，就把title设为当前页面的链接的title
        # item['text'] = text

        # 使用readability解析
        try:
            article = Document(response.text)
            text = article.summary()
            text = re.sub('<.*?>', '', text).strip()
            title = article.title().strip() if article.title().strip() else response.meta['link_title']
        except Exception as e:
            print('item 空', e)
            title = ''
            text = ''
        item['title'] = title
        item['text'] = text

        if text:
            selector = Selector(response)

            structure = selector.xpath('//*[contains(text(), "位置")]/*/text()').extract()  # 查找当前页面所在整个网站的位置，即导航
            if not structure:
                structure = selector.xpath('//*[contains(text(), "位置")]/following-sibling::*/text()').extract()
            structure = [re.sub('\W+', '', s).strip() for s in structure]
            structure = list(filter(lambda s: s and s.strip(), structure))
            structure = '-'.join(structure)
            item['structure'] = structure

            a_tags = selector.xpath('//a[@href]')
            if a_tags:
                attachments_dict = {}  # {url1: title2, url2: title2, ...}
                for tag in a_tags:
                    link = tag.xpath('@href').extract_first()
                    if not str.startswith(link, '#') and 'error' not in link:
                        link = parse.urljoin(HOST, link)
                        try:
                            assert get_tld(link) == self.domain  # 只要本域下的链接
                        except Exception as e:
                            continue
                        else:
                            try:
                                link_title = tag.xpath('@title').extract_first()  # 找a标签内的title
                                if not link_title:
                                    link_title = ''.join(tag.xpath('.//text()').extract())
                                    if not link_title:
                                        raise Exception
                            except Exception as e:
                                link_title = ''
                            else:
                                link_title = link_title.replace('/', '-')

                            link_type = link.split('.')[-1].strip().lower()
                            if link_type in \
                                    ['doc', 'docx', 'ppt', 'pptx', 'pdf', 'xls', 'xlsx', 'txt', 'zip', 'rar', 'png', 'jpg']:
                                # 如果链接是个附件，则保存附件相关信息
                                attachments_dict[link] = link_title
                                if link not in self.attachment_link:
                                    self.attachment_link.add(link)
                                    attachment = AttachmentItem()
                                    attachment['link'] = link
                                    attachment['title'] = link_title
                                    yield attachment
                            else:
                                # 如果链接不是附件，则把链接加入待抓取队列
                                if parse.urlparse(link).netloc in [self.domain, 'www.' + self.domain]:
                                    yield Request(url=link, meta={'link_title': link_title}, callback=self.parse_item)  # 去解析链接
                if attachments_dict:
                    item['attachment'] = json.dumps(attachments_dict, ensure_ascii=False)
            yield item
