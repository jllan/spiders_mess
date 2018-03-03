import random
import re
import time
import requests
from lxml import etree
from pymongo import MongoClient
from multiprocessing.dummy import Pool


client = MongoClient('localhost', 27017)
db = client['data']
proxy_pool = db['proxies']


class ProxyPool():
    def __init__(self):
        pass

    def get_xici(self):
        """抓取xici代理"""
        print('从xici抓取代理')
        results = set()
        url = 'http://www.xicidaili.com/nn/{}'
        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Host': 'www.xicidaili.com',
            'Connection': 'keep-alive',
            'If-None-Match': 'W/"39dde664bf22199337c2ad1788bb7bd5"',
            'Referer': 'http://www.xicidaili.com/nn/2',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36'
        }
        for page in range(1, 4):
            try:
                response =  requests.get(url.format(page), headers=headers)
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
                        protocol = ip.xpath('td[6]/text()')[0].lower()
                        proxy = '{}://{}:{}'.format(protocol, ipaddr, port)
                        # proxy = {'proxy': proxy, 'error_count': 0}
                        results.add(proxy)
                        # self.update_proxy({'proxy': proxy, 'error_count': 0})
        return results


    def get_goubanjia(self):
        """抓取goubanjia代理，有反爬措施，注意端口号"""
        print('从goubanjia抓取代理')
        results = set()
        url = 'http://www.goubanjia.com/free/gngn/index{}.shtml'
        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Host': 'www.goubanjia.com',
            'Connection': 'keep-alive',
            'Referer': 'http://www.goubanjia.com/free/gngn/index.shtml',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36'
        }
        for i in range(1, 4):
            try:
                response = requests.get(url.format(i), headers=headers)
                if response.status_code != 200:
                    raise Exception
            except Exception:
                pass
            else:
                response = etree.HTML(response.text)
                ip_list = response.xpath('//table[@class="table"]/tbody/tr')
                if ip_list:
                    for ip in ip_list:
                        ipaddr = ip.xpath('td[@class="ip"]/span/text()|td[@class="ip"]/div/text()')
                        ipaddr = ''.join(ipaddr[:-1])
                        port = ip.xpath('td[@class="ip"]/span[contains(@class, "port")]/@class')[0]
                        port = port.split()[-1].strip()
                        port = int(''.join((map(str, ['ABCDEFGHIZ'.index(i) for i in port]))))
                        port = port>>3
                        protocol = ip.xpath('td[3]/a/text()')[0]
                        proxy = '{}://{}:{}'.format(protocol, ipaddr, port)
                        results.add(proxy)
                        # self.update_proxy({'proxy': proxy, 'error_count': 0, 'used_latest_time': 0})
        return results

    def get_66ip(self):
        """抓取66ip代理"""
        print('从66ip抓取代理')
        results = set()
        url = 'http://www.66ip.cn/nmtq.php'
        pt = [0, 1]  # 0-http, 1-https
        at = [2, 3, 4]  # 2-普通匿名，3-高级匿名，4-超级匿名
        params = {
            'getnum': 20,
            'isp': 0,
            # 'anonymoustype': at,
            'area': 0,
            # 'proxytype': pt,
            'api': '66ip'
        }
        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Cache-Control': 'max-age=0',
            'Host': 'www.66ip.cn',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36'
        }
        for a in at:
            for p in pt:
                params['anonymoustype'] = a
                params['proxytype'] = p
                try:
                    response = requests.get(url, headers=headers, params=params)
                    if response.status_code != 200:
                        raise Exception
                except Exception:
                    pass
                else:
                    ip_list = re.findall('(\d.*?)<br />', response.text)
                    if ip_list:
                        for ip in ip_list:
                            protocol = 'http' if p==0 else 'https'
                            proxy = '{}://{}'.format(protocol, ip)
                            results.add(proxy)
        return results


    def download_proxy(self):
        proxies = set()
        for target in [self.get_xici, self.get_goubanjia, self.get_66ip]:
            proxies.update(target())
        proxies = [{'proxy': proxy, 'error_count': 0} for proxy in proxies if proxy]
        with Pool() as pool:
            pool.map(self.update_proxy, proxies)

    def update_proxy(self, proxy):
        """
        测试后更新代理，主要更新代理的出错次数
        :param proxy: 要被更新的代理,格式为{'proxy': proxy, 'error_count': 0}
        :param error_count: 代理出错次数
        """
        proxy = self._test_proxy(proxy)
        if proxy['error_count'] >= 1:
            self._del_proxy(proxy)
        else:
            proxy_pool.find_one_and_update(
                {'proxy': proxy['proxy']},
                {'$set': proxy
                 },
                upsert=True
            )
            return proxy

    def _del_proxy(self, proxy):
        proxy_pool.find_one_and_delete(
            {'proxy': proxy['proxy']}
        )

    def _test_proxy(self, proxy):
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
        else:
            print(proxy['proxy'], '有效')
            proxy['error_count'] = 0 if proxy['error_count'] == 0 else (proxy['error_count']-1)
        # self.update_proxy(**proxy)
        return proxy

    def run(self):
        print('启动代理服务......................................................................')
        while True:
            proxies1 = proxy_pool.find({'error_count': {"$lt": 1}}, {'_id': 0})
            proxy_pool.remove({'error_count': {"$gte": 1}})
            print('当前代理池中出错次数小于1的代理数量为：{}'.format(proxies1.count()))
            if proxies1.count() < 20:
                self.download_proxy()
            else:
                time.sleep(60)

            # 多线程测试代理的可用性，只测试出错次数<1的代理，其余的代理认为已经失效
            with Pool(4) as pool:
                pool.map(self.update_proxy, proxies1)


def get_proxy_available():
    proxy_list = [p['proxy'] for p in proxy_pool.find({'error_count':{"$lt": 1}}, {'_id': 0})]
    proxy = random.choice(proxy_list)
    return proxy


def main():
    proxy_pool = ProxyPool()
    proxy_pool.run()


if __name__ == '__main__':
    main()
    # pp = ProxyPool()
    # pp.download_proxy()