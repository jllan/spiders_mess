import random
import json
import time
import requests
from lxml import etree
from pymongo import MongoClient
from threading import Thread
from multiprocessing.dummy import Pool


# api = ''
client = MongoClient('localhost', 27017)
db = client['ProxyPool']
proxy_pool = db['proxies']


class ProxyPool():
    def __init__(self):
        pass

    def get_xici(self, url):
        """
        抓取xici代理
        :param url:
        :return:
        """
        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Cookie': '_free_proxy_session=BAh7B0kiD3Nlc3Npb25faWQGOgZFVEkiJTZkN2I2MjM2NWI1Yzc3OTRjYWM4ZDhhODM0OTc2NjRjBjsAVEkiEF9jc3JmX3Rva2VuBjsARkkiMS9nVkdUR2hkbTFzd29ickROUDFidS9WN1hkalFPbTBmZUhvbzJnVUtDVGc9BjsARg%3D%3D--5d66646a97cb5dbdf92cccdbd1bfe3eedc52c10f; Hm_lvt_0cf76c77469e965d2957f0553e6ecf59=1511420409; Hm_lpvt_0cf76c77469e965d2957f0553e6ecf59=1511514368',
            'Host': 'www.xicidaili.com',
            'Proxy-Connection': 'keep-alive',
            'Referer': 'http://www.xicidaili.com/nn/2',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36'
        }
        try:
            response =  requests.get(url, headers=headers)
            if response.status_code!=200:
                raise Exception
        except Exception:
            pass
        else:
            response = etree.HTML(response.text)
            ip_list = response.xpath('//table[@id="ip_list"]')
            ip_list = ip_list[0].xpath('tr')
            if ip_list:
                for ip in ip_list[1:]:
                    ipaddr = ip.xpath('td[2]/text()')[0]
                    port = ip.xpath('td[3]/text()')[0]
                    # item['address'] = ip.xpath('string(td[4])')[0]
                    protocol = ip.xpath('td[6]/text()')[0].lower()
                    proxy = '{}://{}:{}'.format(protocol, ipaddr, port)
                    print(proxy)
                    self.update_proxy(proxy)

    def download_proxy(self):
        """
        开始抓取代理，代理源网站包括xici等
        :return:
        """
        for i in range(1, 10):
            url = 'http://www.xicidaili.com/nn/{}'.format(i)
            self.get_xici(url)

    def update_proxy(self, proxy, error_count=0):
        """
        测试后更新代理，主要更新代理的出错次数
        :param proxy: 被要更新的代理
        :param error_count: 代理出错次数
        :return:
        """
        proxy_pool.find_one_and_update(
            {'proxy': proxy},
            {'$set':
                 {'proxy': proxy,'error_count': error_count}
             },
            upsert=True
        )
        return proxy

    def _del_proxy(self, proxy):
        proxy_pool.find_one_and_delete(
            {'proxy': proxy}
        )

    def test_proxy(self, proxy):
        test_url = 'http://httpbin.org/ip' # 使用代理请求该地址进行测试
        protocol = proxy['proxy'].split('://')[0]
        proxies = {protocol: proxy['proxy']}
        try:
            res = requests.get(test_url, proxies=proxies, timeout=30)
            if res.status_code != 200:
                raise Exception('请求出错')
            if res.json()['origin'] not in proxy['proxy']:
                raise Exception('代理无效')
        except Exception as e:
            print(proxy['proxy'], e)
            proxy['error_count'] += 1
            if proxy['error_count'] > 5:
                self._del_proxy(proxy)
                return False
        else:
            print(proxy['proxy'], '有效')
            proxy['error_count'] = 0 if proxy['error_count'] == 0 else (proxy['error_count']-1)
        self.update_proxy(**proxy)
        return proxy

    def run(self):
        print('开始ProxyPool.............................................')
        while True:
            # 当代理池中有效代理代理数量<10的时候开始抓取新的代理
            proxies1 = proxy_pool.find({'error_count': {"$lt": 1}}, {'_id': 0})
            proxies3 = proxy_pool.find({'error_count': {"$lt": 3}}, {'_id': 0})
            print('当前pool中出错次数小于1的代理数量为：{}；出错次数小于3的代理数量为：{}'.format(proxies1.count(), proxies3.count()))
            if proxies1.count() < 10:
                self.download_proxy()
            else:
                time.sleep(60)

            # 多线程测试代理的可用性，只测试出错次数<3的代理，其余的代理认为已经失效
            pool = Pool(4)
            pool.map(self.test_proxy, proxies3)
            pool.close()
            pool.join()


def get_proxy_available():
    proxy_list = [p['proxy'] for p in proxy_pool.find({'error_count':{"$lt": 1}}, {'_id': 0})]
    proxy = random.choice(proxy_list)
    print(proxy)
    return proxy


def main():
    proxy_pool = ProxyPool()
    proxy_pool.run()


if __name__ == '__main__':
    main()
    # get_proxy()
    # proxy_test = ProxyTest()
    # proxy_test.run()
    # print(proxy)