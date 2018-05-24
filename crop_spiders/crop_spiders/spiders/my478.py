import re
import scrapy
from urllib import parse
from scrapy.http import Request
from scrapy.selector import Selector
from crop_spiders.items import CropItem

class My478(scrapy.Spider):
    name = "my478"
    allowed_domains = ["my478.com"]
    # start_urls = (
    #     'http://www.my478.com/more/get_tags.php?id=4&page=1',
    # )

    crops = [
        {'crop': '小麦', 'id': 3, 'pages': 80},
        {'crop': '水稻', 'id': 5, 'pages': 80},
        {'crop': '玉米', 'id': 4, 'pages': 80}
    ]

    headers = {
        'Accept': '*/*',
        'Accept-Encoding': 'gzip, deflate, sdch',
        'Accept-Language': 'zh-CN,zh;q=0.8',
        'Connection': 'keep-alive',
        # 'Cookie': 'UM_distinctid=15cec97507817c-06d96efa69673a-38750f56-140000-15cec97507920c; CNZZDATA5626149=cnzz_eid%3D356698111-1498617593-null%26ntime%3D1499784410',
        'Host': 'www.my478.com',
        'Referer': 'http://www.my478.com/html/xiaomai/',
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36',
        'X-Requested-With': 'XMLHttpRequest'
    }

    def start_requests(self):
        for crop in self.crops:
            for page in range(1, crop['pages']+1):
                url = 'http://www.my478.com/more/get_tags.php?id={}&page={}'.format(crop['id'], page)
                yield Request(url=url, headers=self.headers, meta={'crop': crop['crop']}, callback=self.parse_index)

    def parse_index(self, response):
        selector = Selector(response)
        titles = selector.xpath('//li/a/text()').extract()
        urls = selector.xpath('//li/a/@href').extract()
        pub_dates = selector.xpath('//li/span/text()').extract()
        crop = response.meta['crop']
        for title, pub_date, url in zip(titles, pub_dates, urls):
            item = CropItem()
            item['source'] = 'my478'
            item['crop'] = crop
            item['title'] = title
            item['pub_date'] = pub_date
            item['url'] = parse.urljoin('http://www.my478.com', url)
            yield Request(url=item['url'], meta={'item': item}, headers=self.headers, callback=self.parse_detail)

    def parse_detail(self, response):
        item = response.meta['item']
        selector = Selector(response)
        content = selector.xpath('//div[@class="txt"]').extract()
        item['content'] = content
        yield item
