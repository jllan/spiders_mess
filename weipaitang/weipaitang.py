import requests
import re
import time
import random
from lxml import etree
from pymongo import MongoClient
from urllib.parse import urljoin

class WeiPaiTang:
    def __init__(self):
        self.url = 'http://w.weipaitang.com/'
        client = MongoClient('localhost', 27017)
        db = client['paimaitang']
        self.collection = db['paimaitang']

    def down_data(self, page=1, url=None):
        time.sleep(random.random()*5)
        params = {
            'ajax': 'true',
            'page': page
        }
        if not url:
            url = 'http://w.weipaitang.com/wpt/index'
        else:
            url = url
            params['table'] = 'home'
        try:
            response = requests.get(url, params=params)
        except Exception as e:
            print(e)
            return None
        return response.text

    def parse_user(self, data):
        dom = etree.HTML(data)
        res = dom.xpath('//div[contains(@class, "saleItem")]')
        users = []
        for i in res:
            user = {}
            user['url'] = urljoin(self.url, i.xpath('div[@class="avatar"]/a/@href')[0])
            user['_id'] = user['url'].split('/')[-1]
            avatar = i.xpath('div[@class="avatar"]/a/div[@class="avatarImage"]/@style')[0]
            avatar = re.findall('background-image: url\((.*?)\)', avatar)[0]
            user['avatar'] = avatar
            user['name'] = ''.join(i.xpath('div[@class="saleInfo"]/div[@class="nickname"]/a/text()')).strip()
            print(user)
            users.append(user)
        return users

    def parse_sale(self, data):
        dom = etree.HTML(data)
        res = dom.xpath('//div[@class="saleItem"]')
        sales = []
        for i in res:
            sale = {}
            # sale_url = i.xpath('@saleUri')[0]
            sale['sale_id'] = eval(i.xpath('@statistic')[0])['data']['u']
            sale['sale_desc'] = ''.join(i.xpath('div[@class="saleDesc"]/text()')).strip()
            sale['sale_price'] = i.xpath('div[@class="saleInfo"]/div[@class="bid"]/span/text()')[0]
            sales.append(sale)
        return sales


    def save_data(self, item):
        self.collection.find_one_and_update(
            {'_id': item['_id']},
            {'$set':
                 {'url': item['url'], 'avatar': item['avatar'], 'name': item['name'], 'sales': item['sales']}
            },
            upsert=True
        )

    def run(self):
        for i in range(1, 10):
            user_data = self.down_data(page=i)
            # print(user_data)
            if user_data:
                user_items = self.parse_user(user_data)
                print(user_items)
                for user_item in user_items:
                    j = 1
                    user_item['sales'] = []
                    while True:
                        print('url:{}, name:{}, page:{}, '.format(user_item['url'], user_item['name'], j))
                        sale_data = self.down_data(url=user_item['url'], page=j)
                        if sale_data:
                            # print(sale_data)
                            sale_items = self.parse_sale(sale_data)
                            user_item['sales'].append(sale_items)
                            # print(sale_items)
                            j = j+1
                        else:
                            break
                        self.save_data(user_item)


if __name__ == '__main__':
    wpt = WeiPaiTang()
    wpt.run()