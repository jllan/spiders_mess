import requests
import re
import time
import random
from pymongo import MongoClient
from requests.adapters import HTTPAdapter
from requests.packages.urllib3 import Retry
# from requests.packages.urllib3.util import Retry


client = MongoClient('localhost', 27017)
db = client['data']
proxy_pool = db['proxies']


def get_proxy_available():
    proxy_list = [p['proxy'] for p in proxy_pool.find({'error_count': 0}, {'_id': 0})]
    proxy = random.choice(proxy_list)
    print(proxy)
    return proxy

class Shixin:
    def __init__(self):
        client = MongoClient('127.0.0.1', 27017)
        db = client['data']
        self.collection = db['shixin']
        self.url = 'https://sp0.baidu.com/8aQDcjqpAAV3otqbppnN2DJv/api.php'
        self.s = requests.Session()
        retries = Retry(total=3,
                        backoff_factor=0.1,
                        status_forcelist=[404, 500, 502, 503, 504])
        self.s.mount('http://', HTTPAdapter(max_retries=retries))

    def request(self, page):
        headers = {
            'Accept': '*/*',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Connection': 'keep-alive',
            'Cookie': 'BAIDUID=31EC4645FE03EC4F9256E4E35B733D40:FG=1; BIDUPSID=31EC4645FE03EC4F9256E4E35B733D40; PSTM=1511321252; MCITY=-315%3A; BDORZ=B490B5EBF6F3CD402E515D22BCDA1598; H_PS_PSSID=1445_24866_21109_17001_25178; PSINO=3',
            'Host': 'sp0.baidu.com',
            'Referer': 'https://www.baidu.com/s?ie=UTF-8&wd=%E5%A4%B1%E4%BF%A1%E4%BA%BA%E5%91%98%E5%90%8D%E5%8D%95%E6%9F%A5%E8%AF%A2',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36'
        }
        current_time = round(time.time()*1000)
        params = {
            'resource_id': '6899',
            'query': '失信人员名单查询',
            'pn': str(page*10),
            'rn': '10',
            'ie': 'utf-8',
            'oe': 'utf-8',
            'format': 'json',
            't': str(current_time),
            'cb': 'jQuery1102036150306091325435_1517477333487',
            '_': str(current_time-random.randint(0, 10000))
        }
        try:
            proxy = get_proxy_available()
            proxies = {proxy.split(':')[0]: proxy}
            print(proxy)
            res = self.s.get(self.url, headers=headers, params=params, proxies=proxies)
            print(res.status_code)
            if res.status_code != 200:
                raise Exception('使用代理{}请求失败'.format(proxy))
        except Exception as e:
            print('Error: ', e)
            return None
        else:
            print(res.text)
            return res.text

    def parse_data(self, data):
        data = re.findall('\((\{.*?\})\)', data)[0]
        data = eval(data)
        data = data['data'][0]['result']
        print(data)
        print(len(data))
        for d in data:
            item = {}
            print(d)
            item['_id'] = d['cardNum'].strip() # 身份证号
            item['name'] = d['iname'].strip()
            item['businessEntity'] = d['businessEntity'].strip()
            item['age'] = d['age'].strip()
            item['sex'] = d['sexy'].strip()
            item['area'] = d['areaName'].strip()
            item['court_name'] = d['courtName'].strip() # 执行法院
            item['reg_date'] = d['regDate'].strip() # 立案时间
            item['pub_date'] = re.sub('[年月日]', '', d['publishDate']).strip() # 发布时间
            item['gist_id'] = d['gistId'].strip() # 执行依据文号
            item['case_code'] = d['caseCode'].strip() # 案号
            item['gist_unit'] = d['gistUnit'].strip() # 做出执行依据单位
            item['duty'] = d['duty'].strip()  # 生效法律文书确定的义务
            item['performance'] = d['performance'].strip() # 被执行人的履行情况
            item['performed_part'] = d['performedPart'].strip() # 已履行
            item['unperform_part'] = d['unperformPart'].strip() # 未履行
            item['disrupt_type'] = d['disruptTypeName'].strip() # 失信被执行人行为具体情形
            # print(item)
            self.save_data(item)

    def save_data(self, item):
        self.collection.find_one_and_update(
            {'_id': item['_id']},
            {'$set': item},
            upsert=True
        )

    def main(self):
        for i in range(1000):
            data = self.request(i)
            if data:
                self.parse_data(data)


if __name__ == '__main__':
    shixin = Shixin()
    shixin.main()