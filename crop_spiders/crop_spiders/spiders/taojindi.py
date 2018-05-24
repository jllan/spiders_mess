import re
import scrapy
from urllib import parse
from scrapy.http import Request
from scrapy.selector import Selector
from crop_spiders.items import CropItem

class Taojindi(scrapy.Spider):
    name = "taojindi"
    allowed_domains = ["taojindi.com"]

    crops = [
        {'crop': '小麦', 'id': 48, 'pages': 4},
        {'crop': '水稻', 'id': 47, 'pages': 4},
        {'crop': '玉米', 'id': 50, 'pages': 13}
    ]

    headers = {
        'Accept': '*/*',
        'Accept-Encoding': 'gzip, deflate, sdch',
        'Accept-Language': 'zh-CN,zh;q=0.8',
        'Connection': 'keep-alive',
        # 'Cookie': 'UM_distinctid=15cec97507817c-06d96efa69673a-38750f56-140000-15cec97507920c; CNZZDATA5626149=cnzz_eid%3D356698111-1498617593-null%26ntime%3D1499784410',
        'Host': 'nongye.taojindi.com',
        'Referer': 'http://nongye.taojindi.com/ask/list_47.html',
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36',
        'Upgrade-Insecure-Requests': '1'
    }

    def start_requests(self):
        for crop in self.crops:
            for page in range(1, crop['pages']+1):
                url = 'http://nongye.taojindi.com/ask/list_{}_{}.html'.format(crop['id'], page)
                yield Request(url=url, headers=self.headers, meta={'crop': crop['crop']}, callback=self.parse_index)

    def parse_index(self, response):
        selector = Selector(response)
        qs = selector.xpath('//tr')[1:]
        crop = response.meta['crop']
        for q in qs:
            item = CropItem()
            title = q.xpath('./td[@class="td-tit"]/a//text()').extract()[1]
            url = q.xpath('./td[@class="td-tit"]/a/@href').extract_first()
            pub_date = q.xpath('./td[4]/text()').extract_first()
            item['source'] = 'taojindi'
            item['crop'] = crop
            item['title'] = title
            item['pub_date'] = pub_date
            item['url'] = url
            # print(item)
            yield Request(url=item['url'], meta={'item': item}, headers=self.headers, callback=self.parse_detail)

    def parse_detail(self, response):
        item = response.meta['item']
        selector = Selector(response)
        content = selector.xpath('//div[@class="satisfactory-answer"]').extract() # 保留原有格式
        # content = selector.xpath('//div[@class="satisfactory-answer"]').xpath('string(.)').extract_first() # 提取出所有文字，忽略原有的格式
        item['content'] = content
        yield item
