# coding: utf8

# @Source: 南京市农业委员会
# @Description: 数据较多，每种作物分为栽培技术、病虫防治、对症下药（具体每种病虫害、杂草对应的防治药物，这一部分没抓取），
#               并且每天都有更新，首次全爬，以后增量爬取，每次爬前10页。


from urllib.parse import urljoin
import scrapy
from scrapy.http import Request
from scrapy.selector import Selector
from crop_spiders.items import CropItem

class Njaf(scrapy.Spider):
    name = "njaf"
    # allowed_domains = ["njaf.gov.cn"]

    crops = [
        # {'crop': '水稻', 'type': '栽培技术', 'pages': 1},
        {'crop': '水稻', 'type': '栽培技术', 'pages': 164},
        {'crop': '水稻', 'type': '病虫防治', 'pages': 40},
        {'crop': '小麦', 'type': '栽培技术', 'pages': 214},
        {'crop': '小麦', 'type': '病虫防治', 'pages': 38},
        {'crop': '玉米', 'type': '栽培技术', 'pages': 278},
        {'crop': '小麦', 'type': '病虫防治', 'pages': 27}
    ]

    headers = {
        'Accept': '*/*',
        'Accept-Encoding': 'gzip, deflate, sdch',
        'Accept-Language': 'zh-CN,zh;q=0.8',
        'Connection': 'keep-alive',
        'Host': 'www.agri114.cn',
        'Referer': 'http://www.agri114.cn/njaf_cmp/page/lymh/index.jsp',
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36',
        'Upgrade-Insecure-Requests': '1'
    }

    def start_requests(self):
        for crop in self.crops:
            for page in range(1, crop['pages']+1):
                # time.sleep(random.random()*10)
                url = 'http://www.agri114.cn/njaf_cmp/lymh/showListByCategory.action?category={}&type={}&pageNo={}'.format(crop['crop'], crop['type'], page)
                yield Request(url=url,
                              headers=self.headers,
                              # body=urlencode({'category':crop['crop'], 'type':crop['type'], 'pageNo':page}),
                              meta={'crop': crop['crop']},
                              callback=self.parse_index)

    def parse_index(self, response):
        selector = Selector(response)
        qs = selector.xpath('//div[@class="list_li"]/ul//li')
        crop = response.meta['crop']
        for q in qs:
            item = CropItem()
            title = q.xpath('./a//text()').extract_first()
            url = urljoin('http://www.agri114.cn', q.xpath('./a/@href').extract_first())
            pub_date = q.xpath('./span/text()').extract_first()
            item['source'] = 'njaf'
            item['crop'] = crop
            item['title'] = title
            item['url'] = url
            item['pub_date'] = pub_date
            # print(item)
            yield Request(url=item['url'], meta={'item': item}, headers=self.headers, callback=self.parse_detail)

    def parse_detail(self, response):
        # time.sleep(random.random() * 5)
        item = response.meta['item']
        selector = Selector(response)
        content = selector.xpath('//div[@class="neirong"]').extract() # 保留原有格式
        item['content'] = content
        print(item)
        yield item
