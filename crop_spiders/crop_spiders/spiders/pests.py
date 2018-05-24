# !/usr/bin/python3

# coding:utf8
# @Author: Jlan
# @Time: 17-8-29 下午10:46

# @Source: 中国农业有害生物信息系统 http://pests.agridata.cn/base.asp
# @Description: 数据分为病害、虫害、杂草等

import re
import time
import random
from urllib.parse import urljoin
import scrapy
from scrapy.http import Request
from scrapy.selector import Selector
from crop_spiders.items import PestItem


class Pests(scrapy.Spider):
    name = "pests"
    # allowed_domains = ["http://pests.agridata.cn"]

    pests = [
        # {'base_name': '粮食作物病毒病害', 'type': '病害', 'id': '13', 'pages': 2},
        # {'base_name': '粮食作物细菌病害', 'type': '病害', 'id': '12', 'pages': 2},
        # {'base_name': '粮食作物真菌病害', 'type': '病害',  'id': '11', 'pages': 12},
        # {'base_name': '旱粮作物害虫', 'type': '虫害',  'id': '5', 'pages': 9},
        {'base_name': '水稻害虫', 'type': '虫害',  'id': '3', 'pages': 3},
        # {'base_name': '旱地杂草', 'type': '杂草',  'id': '20', 'pages': 7},
        # {'base_name': '水田杂草', 'type': '杂草',  'id': '19', 'pages': 4},
        # {'base_name': '农田害鼠', 'type': '虫害', 'id': '17', 'pages': 2},
        # {'base_name': '经济作物病毒病害', 'type': '病害', 'id': '16', 'pages': 5},
        # {'base_name': '经济作物细菌病害', 'type': '病害', 'id': '15', 'pages': 5},
        # {'base_name': '经济作物真菌病害', 'type': '病害', 'id': '14', 'pages': 31},
        # {'base_name': '果类蔬菜害虫', 'type': '虫害', 'id': '8', 'pages': 4},
        # {'base_name': '果类蔬菜害虫', 'type': '虫害', 'id': '6', 'pages': 3},
        # {'base_name': '果类蔬菜害虫', 'type': '虫害', 'id': '9', 'pages': 6},
        # {'base_name': '果类蔬菜害虫', 'type': '虫害', 'id': '10', 'pages': 4},
        # {'base_name': '棉花害虫', 'type': '虫害', 'id': '4', 'pages': 3},
        # {'base_name': '外来入侵植物', 'type': '杂草', 'id': '23', 'pages': 12},
        # {'base_name': '外来入侵昆虫', 'type': '虫害', 'id': '22', 'pages': 5},
        # {'base_name': '外来入侵微生物', 'type': '病害', 'id': '21', 'pages': 3}
    ]

    headers = {
        'Accept': '*/*',
        'Accept-Encoding': 'gzip, deflate, sdch',
        'Accept-Language': 'zh-CN,zh;q=0.8',
        'Connection': 'keep-alive',
        'Host': 'pests.agridata.cn',
        'Referer': 'http://pests.agridata.cn/base.asp',
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36',
        'Upgrade-Insecure-Requests': '1',
        'DNT': '1'
    }

    def start_requests(self):
        for pest in self.pests:
            for page in range(1, pest['pages']+1):
                time.sleep(random.random()*5)
                url = 'http://pests.agridata.cn/base{}.asp?page={}'.format(pest['id'], page)
                yield Request(url=url,
                              headers=self.headers,
                              meta={'type': pest['type']},
                              callback=self.parse_index)

    def parse_index(self, response):
        selector = Selector(response)
        qs = selector.xpath('//table[@class="textcss"]/tr/td[5]/a')
        for q in qs:
            item = PestItem()
            name = q.xpath('./text()').extract_first()
            link = urljoin('http://pests.agridata.cn/', q.xpath('./@href').extract_first())
            # print(name, link)
            item['name'] = name
            item['url'] = link
            item['type'] = response.meta['type']
            item['source'] = '中国农业科学院植物保护研究所'

            yield Request(url=item['url'], meta={'item': item}, headers=self.headers, callback=self.parse_detail)

    def parse_detail(self, response):
        # time.sleep(random.random() * 5)
        item = response.meta['item']
        # print(item)
        p_img = re.compile('(showimg.*?id=\d+)')
        img = re.search(p_img, response.text).group()
        print('图片地址', img)
        p_alias = re.compile('别名：.*?<font.*?>(.*?)</font>', re.S)
        # p_pathogen_name = re.compile('病原中文名：.*?<font.*?>(.*?)</font>', re.S)
        p_harm_crop = re.compile('(主要危害作物|寄主)：.*?<font.*?>(.*?)</font>', re.S)
        p_harm_position = re.compile('主要为害部位：.*?<font.*?>(.*?)</font>', re.S)
        p_pest_feature = re.compile('(为害症状|形态特征)：.*?<font.*?>(.*?)</font>', re.S)
        p_spread_and_occur = re.compile('(传播途径和发病条件|发生与危害|生物学特性及发生消长规律|发生消长规律)：.*?<font.*?>(.*?)</font>', re.S)
        p_prevention = re.compile('(防治方法|综合治理策略|控制方法)：.*?<font.*?>(.*?)</font>', re.S)
        p_zone = re.compile('(地理分布|入侵地)：.*?<font.*?>(.*?)</font>', re.S)
        alias = re.findall(p_alias, response.text)
        # pathogen_name = re.findall(p_pathogen_name, response.text)
        harm_position = re.findall(p_harm_position, response.text)
        try:
            harm_crop = re.search(p_harm_crop, response.text).group(2)
        except Exception as e:
            harm_crop = ''
        try:
            pest_feature = re.search(p_pest_feature, response.text).group(2)
        except Exception as e:
            pest_feature = ''
        try:
            spread_and_occur = re.search(p_spread_and_occur, response.text).group(2)
        except Exception as e:
            spread_and_occur = ''
        try:
            prevention = re.search(p_prevention, response.text).group(2)
        except Exception as e:
            prevention = ''
        try:
            zone = re.search(p_zone, response.text).group(2)
        except Exception as e:
            zone = ''
        # print(harm_crop)
        # print(harm_position)
        # print(pest_feature)
        # print(spread_and_occur)
        # print(prevention)
        # print(zone)
        item['img'] = urljoin('http://pests.agridata.cn', img)
        item['alias'] = ''.join(alias) if alias else ''
        # item['pathogen_name'] = ''.join(pathogen_name) if alias else ''
        item['harm_crop'] = ''.join(harm_crop) if harm_crop else ''
        item['harm_position'] = ''.join(harm_position) if harm_position else ''
        item['pest_feature'] = ''.join(pest_feature)
        item['spread_and_occur'] = ''.join(spread_and_occur)
        item['prevention'] = ''.join(prevention)
        item['zone'] = ''.join(zone) if zone else ''
        print(item)
        yield item
