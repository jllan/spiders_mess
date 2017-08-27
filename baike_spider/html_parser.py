#coding:utf-8
from bs4 import BeautifulSoup
import re
import urllib.parse

class HtmlParser:

    def __init__(self):
        pass

    def _get_urls(self, page_url, soup):
        new_urls = set()
        '''/view/21087.htm'''
        links = soup.findAll('a', href=re.compile('view/\d+\.htm'))
        for link in links:
            # print(link)
            url = urllib.parse.urljoin(page_url, link['href'])
            # url = 'http://baike.baidu.com'+link['href']
            new_urls.add(url)
        return new_urls

    def _get_data(self, page_url, soup):
        data = {}
        # title: <dd class="lemmaWgt-lemmaTitle-title" > <h1>Python</h1>
        title = soup.find('dd', class_="lemmaWgt-lemmaTitle-title").h1.text
        data['title'] = title
        # summary: <div class="lemma-summary" label-module="lemmaSummary">
        summary = soup.find('div', class_="lemma-summary").text
        data['summary'] = summary
        data['url']= page_url
        return data

    def parse(self, page_url, html_content):
        if not page_url or not html_content:
            return
        soup = BeautifulSoup(html_content, 'lxml')
        urls = self._get_urls(page_url, soup)
        data = self._get_data(page_url, soup)
        return (urls, data)

