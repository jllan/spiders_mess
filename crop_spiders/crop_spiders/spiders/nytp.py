# coding: utf8

import time
import random
import requests
from lxml import etree
from pymongo import MongoClient

class Nytp:
    def __init__(self):
        client = MongoClient('localhost', 27017)
        db = client['agri_resource']
        self.pest = db['pest2']


    def request(self, url):
        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Connection': 'keep-alive',
            'Host': 'tupu.zgny.com.cn',
            'Cache-Control': 'max-age=0',
            'Cookie': 'UM_distinctid=15ef6201eeb52f-076594627b87c9-1227170b-100200-15ef6201eec1d1; yunsuo_session_verify=5da0ca256151c57a2f98e02d24945f50; CNZZDATA1262394838=1372932544-1507366400-https%253A%252F%252Fwww.baidu.com%252F%7C1512401045',
            # 'If-Modified-Since': 'Mon, 04 Dec 2017 15:38:15 GMT',
            'Referer': 'http://tupu.zgny.com.cn/Page_1_NodeId_nzwbch_js_shuidao.shtml',
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36',
            'Upgrade-Insecure-Requests': '1'
        }
        try:
            response = requests.get(url, headers=headers)
            # print(response.content)
        except Exception as e:
            print('error: ', e)
            return None
        return response

    def main(self):
        for page in range(1, 2):
            # time.sleep(random.random()*10)
            url = 'http://tupu.zgny.com.cn/Page_{}_NodeId_nzwbch_js_shuidao.shtml'.format(page)
            # print(url)
            data = self.request(url)
            # print(data)
            if data:
                self.parse_index(data)

    def parse_index(self, response):
        doc = etree.HTML(response.text)
        qs = doc.xpath('//ul[@class="home-list3ccc"]/li')
        for q in qs:
            item = {}
            name = q.xpath('./span/a/span/text()')[0]
            url = q.xpath('./span/a/@href')[0]
            item['source'] = 'nytp'
            item['crop'] = '水稻'
            item['name'] = name
            item['url'] = url
            print(item)
            data = self.request(url)
            print('data:', data.content.decode('gbk'))
            if data:
                # time.sleep(random.random() * 5)
                detail = self.parse_detail(data)
                item['detail'] = detail
                # self.pest.insert(item)


    def parse_detail(self, response):
        print(response.content)
        doc = etree.HTML(response.content)
        detail = doc.xpath('//div[@class="conLeft"]') # 保留原有格式
        print('detail')
        print(detail)
        return detail


if __name__ == '__main__':
    nytp = Nytp()
    nytp.main()
