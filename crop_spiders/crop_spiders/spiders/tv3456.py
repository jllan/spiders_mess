import re
import time
import random
from urllib.parse import urljoin
import scrapy
from scrapy.http import Request
from scrapy.selector import Selector
from crop_spiders.items import CropItem

class Tv3456(scrapy.Spider):
    name = "tv3456"
    allowed_domains = ["3456.tv"]

    crops = [
        {'crop': 'liangshi', 'pages': 68} # 网站没有区分具体的作物类别
    ]

    headers = {
        'Accept': '*/*',
        'Accept-Encoding': 'gzip, deflate, sdch',
        'Accept-Language': 'zh-CN,zh;q=0.8',
        'Connection': 'keep-alive',
        'Host': 'ask.3456.tv',
        'Referer': 'http://ask.3456.tv/type_liangshi/1',
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36',
        'Upgrade-Insecure-Requests': '1'
    }

    def start_requests(self):
        for crop in self.crops:
            for page in range(1, crop['pages']+1):
                time.sleep(random.random()*10)
                url = 'http://ask.3456.tv/type_{}/{}'.format(crop['crop'], page)
                yield Request(url=url, headers=self.headers, meta={'crop': crop['crop']}, callback=self.parse_index)

    def parse_index(self, response):
        selector = Selector(response)
        qs = selector.xpath('//div[@class="list"]//li')
        crop = response.meta['crop']
        for q in qs:
            item = CropItem()
            title = q.xpath('./p/a//text()').extract_first()
            url = urljoin('http://ask.3456.tv', q.xpath('./p/a/@href').extract_first())
            item['source'] = 'tv3456'
            item['crop'] = crop
            item['title'] = title
            item['url'] = url
            yield Request(url=item['url'], meta={'item': item}, headers=self.headers, callback=self.parse_detail)

    def parse_detail(self, response):
        time.sleep(random.random() * 5)
        item = response.meta['item']
        selector = Selector(response)
        content = selector.xpath('//div[@class="huid"][1]/*').extract()[:-2] # 只取第一个回答，保留原有格式
        item['content'] = content
        # print(content)
        pub_date_pattern = re.compile('提问时间：(.*?)</span>')
        pub_date = re.findall(pub_date_pattern, response.text)[0].strip() # 日期在答案的倒数第二个p标签内
        item['pub_date'] = pub_date
        yield item
