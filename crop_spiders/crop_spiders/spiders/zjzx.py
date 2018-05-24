import re
import json
import time
import random
from urllib import parse
import scrapy
from scrapy.http import Request
from scrapy.selector import Selector
from crop_spiders.items import CropItem

class My478(scrapy.Spider):
    name = "zjzx"
    allowed_domains = ["zjzx.cnki.net"]
    # start_urls = (
    #     'http://zjzx.cnki.net/BBS/BBSList?code=101001001&codename=%E6%B0%B4%E7%A8%BB',
    # )

    crops = [
        # {'crop': '水稻', 'id': 101001001, 'pages': 1},
        {'crop': '水稻', 'id': 101001001, 'pages': 40},
        # {'crop': '玉米', 'id': 101001002, 'pages': 3067},
        # {'crop': '小麦', 'id': 101001003, 'pages': 2388}
    ]

    headers = {
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'zh-CN,zh;q=0.8',
        'Connection': 'keep-alive',
        # 'Cookie': 'Ecp_ClientId=2170419214102960401; cnkiUserKey=95717522-afa1-9faa-d40a-5bba0d4a3fe4; kc_cnki_net_uid=052cc7bd-c657-8496-594f-83023a9bcc2b; ASP.NET_SessionId=02azaqasuus2jqik1hmt2sns; SID=201077; __RequestVerificationToken=idAUJILP_wFw_Y-b2gVBSgm3UOI77F3LBawp58FT1KT053TOu3bIUp7F8CA8XX-cGGtVkkb-1UfJjDTH8jR7tCjOXZL-M2BBOLgEHUtvz_KXc4NgVmqneuv8xsXnBfXWVzb1BzRa8s18SERBhe16TQ2; UM_distinctid=15fbd96911ca9-0c80ad2f660141-1227170b-140000-15fbd96911d819; wan_id_browse_like=wan_id_browse_like306=2017/11/15 20:24:16; c_m_LinID=LinID=WEEvREcwSlJHSldRa1FhcTdWZDhML1NzY2ZJSXNKNjlKZ0p6amIrTDUyRT0=$9A4hF_YAuvQ5obgVAqNKPCYcEjKensW4IQMovwHtwkF4VYPoHbKxJw!!&ot=11/15/2017 20:49:33; question_id=question_id1001531=2017/11/15 10:52:05&question_id1001174=2017/11/15 10:52:21&question_id1004705=2017/11/15 11:01:02&question_id1004703=2017/11/15 11:04:46&question_id1004482=2017/11/15 11:08:10&question_id1004477=2017/11/15 11:12:33&question_id1004094=2017/11/15 11:12:45&question_id1007360=2017/11/15 20:08:41&question_id1006498=2017/11/15 20:10:07&question_id1006492=2017/11/15 20:10:17&question_id1005745=2017/11/15 20:10:31&question_id1005733=2017/11/15 20:10:38&question_id1004826=2017/11/15 20:11:03&question_id1004663=2017/11/15 20:11:19&question_id1004676=2017/11/15 20:11:57&question_id1003853=2017/11/15 20:12:15&question_id1007480=2017/11/15 20:12:50&question_id1000107=2017/11/15 20:13:00&question_id1000102=2017/11/15 20:13:12&question_id992157=2017/11/15 20:13:23&question_id14257=2017/11/15 20:13:32&question_id1008500=2017/11/15 20:14:36&question_id998518=2017/11/15 20:14:49&question_id996309=2017/11/15 20:25:46&question_id968514=2017/11/15 20:25:52&question_id942770=2017/11/15 20:26:12&question_id937604=2017/11/15 20:26:16&question_id930099=2017/11/15 20:26:32&question_id929973=2017/11/15 20:26:39&question_id1000640=2017/11/15 20:30:28; CNZZDATA1000415762=1455377011-1510409533-http%253A%252F%252Fwww.jianshu.com%252F%7C1510746703',
        'Host': 'zjzx.cnki.net',
        'Referer': 'http://zjzx.cnki.net/BBS/BBSList?code=101001001&codename=%E6%B0%B4%E7%A8%BB',
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36',
        # 'X-Requested-With': 'XMLHttpRequest'
    }

    def start_requests(self):
        headers = self.headers
        headers['X-Requested-With'] = 'XMLHttpRequest'
        for crop in self.crops:
            for page in range(1, crop['pages']+1):
                if page % 100 == 0:
                    time.sleep(random.random()*50)
                params = {
                    'randID': '0.2457507296817134',
                    'code': crop['id'],
                    'codeName': crop['crop'],
                    'currentPageNo': page,
                    # 'mark': '',
                    # 'bbsPaiXuList':
                    # inputsearch:
                    'selectsearch': 'title'
                }
                url = 'http://zjzx.cnki.net/BBS/BBSHtml?' + parse.urlencode(params)
                yield Request(url=url, headers=headers, meta={'crop': crop['crop']}, callback=self.parse_index)

    def parse_index(self, response):
        result = response.text.replace('null', "None")
        result = eval(result)
        crop = response.meta['crop']
        for r in result[0]:
            item = CropItem()
            item['crop'] = crop
            qid = r['ID']
            item['url'] = 'http://zjzx.cnki.net/BBS/BBSDetail?questionID={}'.format(qid)
            item['title'] = r['Title']
            item['pub_date'] = r['PublishDate'].replace('T', ' ')
            item['source'] = 'zjzx'
            headers = self.headers
            headers['Upgrade-Insecure-Requests'] = '1'
            yield Request(url=item['url'], meta={'item': item}, headers=headers, callback=self.parse_detail)

    def parse_detail(self, response):
        # time.sleep(random.random() * 10)
        item = response.meta['item']
        selector = Selector(response)
        try:
            content = selector.xpath('//div[@class="recbox"]')[1].extract()
        except Exception:
            content = ''
        else:
            content = [content]  # 其它几个网站抓取的content都是list
        item['content'] = content
        yield item
