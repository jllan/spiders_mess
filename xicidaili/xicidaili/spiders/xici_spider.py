# -*- coding: utf-8 -*-
import scrapy
import time
from scrapy.http import Request
from xicidaili.items import XicidailiItem


class XiciSpiderSpider(scrapy.Spider):
    name = "xici_spider"
    allowed_domains = ["xicidaili.com"]
    start_urls = (
        'http://www.xicidaili.com/',
        # ['http://www.xicidaili.com/nn/{}'.format(page) for page in range(1, 11)]
    )

    def start_requests(self):
        start = time.time()
        for i in range(1, 50):
            url = 'http://www.xicidaili.com/nn/{}'.format(i)
            yield Request(url, callback=self.parse)
        print('run time:', time.time()-start)

    def parse(self, response):
        ip_list = response.xpath('//table[@id="ip_list"]')
        ip_list = ip_list[0].xpath('tr')
        if ip_list:
            for ip in ip_list[1:]:
                # print(ip)
                item = XicidailiItem()
                item['ip'] = ip.xpath('td[2]/text()')[0].extract()
                item['port'] = ip.xpath('td[3]/text()')[0].extract()
                item['address'] = ip.xpath('string(td[4])')[0].extract().strip()
                item['protocol'] = ip.xpath('td[6]/text()')[0].extract()
                # print(item)
                yield item


