# -*- coding: utf-8 -*-
from scrapy import Spider, Request, FormRequest
from MobaiSpider.items import MobaispiderItem
import numpy as np
import json
import time


class MobaiSpider(Spider):
    name = 'mobai'
    # allowed_domains = ['mobike.com']
    # start_urls = ['http://mobike.com/']
    url = "https://mwx.mobike.com/mobike-api/rent/nearbyBikesInfo.do"


    headers = {
        'charset': "utf-8",
        'platform': "4",
        "referer": "https://servicewechat.com/wx80f809371ae33eda/144/page-frame.html",
        'content-type': "application/x-www-form-urlencoded",
        'user-agent': "MicroMessenger/6.5.4.1000 NetType/WIFI Language/zh_CN",
        'host': "mwx.mobike.com",
        'connection': "Keep-Alive",
        'accept-encoding': "gzip",
        'cache-control': "no-cache",
    }

    def start_requests(self):
        left = 32.2418440767
        top = 118.5623931885
        right = 31.8892185988
        bottom = 119.0059661865

        # 32.2418440767, 118.5623931885 左上
        # 31.8892185988, 119.0059661865 右下

        offset = 0.002

        print("Start")
        self.total = 0
        lat_range = np.arange(left, right, -offset)
        for lat in lat_range:
            lon_range = np.arange(top, bottom, offset)
            for lon in lon_range:
                self.total += 1
                # self.get_nearby_bikes(lat, lon)
                item = MobaispiderItem()
                item['currentX'] = lat
                item['currentY'] = lon
                item['timestamp'] = time.time()
                yield FormRequest(
                    self.url,
                    headers=self.headers,
                    formdata = {
                        'accuracy': '30',
                        'citycode': '025',
                        'errMsg': 'getLocation:ok',
                        'horizontalAccuracy': '30',
                        'latitude': str(lat),
                        'longitude': str(lon),
                        'speed': '-1',
                        'verticalAccuracy': '0',
                        'wxcode': '021Ay5DV0LUt2V1bRUDV0E8ICV0Ay5DN'
                    },
                    callback=self.parse,
                    meta={'item': item}
                )

    def parse(self, response):
        print(response.text)
        data = json.loads(response.text)
        bikes = data['object']
        if bikes:
            for bike in bikes:
                item = response.meta['item']
                item['bikeIds'] = bike['bikeIds']
                item['bikeType'] = bike['biketype']
                item['distX'] = bike['distX']
                item['distY'] = bike['distY']
                item['distId'] = bike['distId']
                item['distance'] = bike['distance']
                item['boundary'] = bike['boundary']
                yield item


