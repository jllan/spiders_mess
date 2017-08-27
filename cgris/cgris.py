import requests
import requests.adapters
from math import ceil
from queue import Queue
import time
import random
from rice_model import Rice, RiceSession
from wheat_model import Wheat, WheatSession


class Cgris:
    def __init__(self, product, province=None):
        self.product = '["粮食作物", "{}"]'.format(product)
        self.province = '{"省": ["%s"]}'%province if province else '{}'
        adapter = requests.adapters.HTTPAdapter(max_retries=5)
        self.session = requests.session()
        self.session.mount('https://', adapter)
        self.session.mount('http://', adapter)
        if product=='小麦':
            self.model = Wheat
            self.db_session = WheatSession
        if product == '水稻':
            self.model = Rice
            self.db_session = RiceSession
        # self.q = Queue()

    def down_data(self, page=0, index=None):
        url = 'http://www.cgris.net/query/o.php'
        headers = {
            'Accept': 'text/javascript, text/html, application/xml, text/xml, */*',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'zh-CN,zh;q=0.8',
            'Connection': 'keep-alive',
            'DNT': '1',
            'Content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
            # 'Cookie': 'ASPSESSIONIDSCBSCBSR=IPAAKCMAODFOGKOFHINPNNOI; PHPSESSID=52caf6c49681ccb44a047975d4b2611b; UM_distinctid=15b159b82cc0-03913d45085b7d-1421150f-140000-15b159b82cd2f1; CNZZDATA1259170489=485182666-1490716164-http%253A%252F%252Fwww.cgris.net%252F%7C1490716164',
            'Host': 'www.cgris.net',
            'Origin': 'http://www.cgris.net',
            'Referer': 'http://www.cgris.net/query/do.php',
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36',
            'X-Prototype-Version': '1.5.1.1',
            'X-Requested-With': 'XMLHttpRequest'
        }
        data = {
            'p': self.province,
            'croptype': self.product,
        }
        # 请求数据
        if index:
            data['action'] = 'item'
            data['p'] = index
        # 请求index第二页以后
        elif page:
            data['action'] = 'queryp'
            data['s'] = str(page)
        # 请求index第一页
        else:
            data['action'] = 'query'
        res = self.session.post(url, headers=headers, data=data)
        print(res.json())
        return res.json()


    # def parse_index(self, index):
    #     for i in index:
    #         self.q.put(i)

    def save_data(self, data):
        db_session = self.db_session()
        new_data = self.model(**data)
        try:
            db_session.add(new_data)
            db_session.commit()
        except Exception as e:
            print('{}插入错误：{}'.format(data['统一编号'], e))
        db_session.close()


    def run(self):
        count, index = self.down_data()
        for i in index:
            item = self.down_data(index=i[0])
            self.save_data(item)
            # time.sleep(random.random()*5)
        pages = ceil(count / 100)
        for page in range(35, pages):
            index = self.down_data(page=page)
            for i in index:
                item = self.down_data(index=i[0])
                self.save_data(item)
                # time.sleep(random.random()*2)
            # time.sleep(random.random() * 10)


if __name__ == '__main__':
    '''
    AREA_INFO = '{"省": ["江苏"]}'
    PRODUCT_INFO = '["粮食作物", "水稻"]'
    '''
    cgris = Cgris("小麦")
    cgris.run()