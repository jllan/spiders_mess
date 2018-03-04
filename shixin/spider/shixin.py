import requests
import os
import re
import random
import time
from pymongo import MongoClient
from captcha_recognition.main import predictt

captcha_dir = '/home/jlan/WorkSpace/cv/dataset/court3'

# 代理池
client = MongoClient('localhost', 27017)
db = client['data']
proxy_pool = db['proxies']


def get_proxy_available():
    """从代理池取出一个代理"""
    proxy_list = [p for p in proxy_pool.find({'error_count': 0}, {'_id': 0})]
    proxy = random.choice(proxy_list)
    # proxy = ''
    print('更新代理为： {}'.format(proxy['proxy']))
    return proxy

class CaptchaError(Exception):
    def __init__(self, err='验证码错误'):
        Exception.__init__(self, err)

class RequestError(Exception):
    def __init__(self, err='网络请求出错'):
        Exception.__init__(self, err)


class Shixin:
    def __init__(self):
        self.collection = db['shixin_court']
        self.url = 'http://shixin.court.gov.cn/findDisNew'
        # self.url = 'http://shixin.court.gov.cn/findDis'
        self.detail_url = 'http://shixin.court.gov.cn/disDetailNew'
        self.captcha_url = 'http://shixin.court.gov.cn/captchaNew.do'
        self.session = requests.Session()
        self.proxy = get_proxy_available()
        self.captcha = self.get_captcha()

    def request(self, name=None, user_id=None, page=1):
        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Connection': 'keep-alive',
            # 'Cookie': '_gscu_2025930969=13060113ovjetd18; _gscu_125736681=1305988048o95912; Hm_lvt_9e03c161142422698f5b0d82bf699727=1513059881,1513146885; _gscbrs_2025930969=1; _gscs_2025930969=t17548934zvvsdu10|pv:4; JSESSIONID=2890F2C81E51A5134E948C8ACF88A710',
            'Host': 'shixin.court.gov.cn',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36'
        }

        if name:
            print('获取姓名前两个字为 “{}” 的第 {} 个列表页，验证码为 {} ，代理为 {} '.format(name, page, self.captcha, self.proxy))
            data = {
                'currentPage': page,
                'pName': name,
                'pCardNum': '',
                'pProvince': '0',
                'pCode': self.captcha,
                'captchaId': '327738a470b843f0960df9f6b2d4a25b'
            }
            headers.update({
                'Referer': 'http://shixin.court.gov.cn/index_new_form.do',
                'Cache-Control': 'max-age=0',
                'Content-Length': '100',
                'Content-Type': 'application/x-www-form-urlencoded',
                'Origin': 'http://shixin.court.gov.cn',
                'Upgrade-Insecure-Requests': '1',
            })
            req = requests.Request('POST', url=self.url, headers=headers, data=data)

        elif user_id:
            print('获取用户 {} 的详细信息，验证码为 {} ，代理为 {} '.format(user_id, self.captcha, self.proxy))
            params = {
                'captchaId': '327738a470b843f0960df9f6b2d4a25b',
                'pCode': self.captcha,
                'id': user_id
            }
            headers.update({
                'Referer': 'http://shixin.court.gov.cn',
                'X-Requested-With': 'XMLHttpRequest'
            })
            req = requests.Request('GET', url=self.detail_url, headers=headers, params=params)

        else:
            print('获取验证码，代理为 {} '.format(self.proxy))
            headers['Referer'] = 'http://shixin.court.gov.cn/index_form.do'
            params = {
                'captchaId': '327738a470b843f0960df9f6b2d4a25b',
                'random': str(random.random())
            }
            req = requests.Request('GET', url=self.captcha_url, headers=headers, params=params)

        prepped = self.session.prepare_request(req)

        proxies = {self.proxy['proxy'].split(':')[0]: self.proxy['proxy']}

        try:
            res = self.session.send(prepped, proxies=proxies, timeout=60)
            if res.status_code != 200:
                raise Exception
            if '验证码错误或验证码已过期，请重新输入！' in res.text:
                raise CaptchaError
        except CaptchaError as e:
            print('Error: {}'.format(e))
            self.captcha = shixin.get_captcha()
            res = self.request(name=name, user_id=user_id, page=page)
            return res
        except RequestError as e:
            print('Error: {}'.format(e))
            return None
        except Exception as e:
            print('Error: {}'.format(e))
            self.proxy = get_proxy_available()
            res = self.request(name=name, user_id=user_id, page=page)
            return res
        else:
            # print('result:', res.text)
            print('success')
            return res

    def get_captcha(self):
        res = self.request()
        captcha_file = self.save_captcha(res.content)
        captcha = self.recognition_captcha(captcha_file)
        print('更新验证码为{}'.format(captcha))
        return captcha

    def recognition_captcha(self, captcha_file):
        pred = predictt(captcha_file)
        return pred

    def save_captcha(self, captcha_data, captcha_title='captcha'):
        captcha_file = os.path.join(captcha_dir, str(captcha_title) + '.jpg')
        with open(captcha_file, 'wb') as f:
            f.write(captcha_data)
        return captcha_file

    def parse_data(self, res):
        try:
            data = res.text
            pages = re.findall('id="pagenum".*?页.*?\d+/(\d+).*?共', data)[0]
            ids = re.findall('class="View".*?id="(\d+)">查看', data)
        except Exception as e:
            print(e)
            pages = ids = None
        return pages, ids

    def parse_detail_data(self, detail_res):
        try:
            detail_data = detail_res.json()
        except Exception as e:
            print(e)
            return None
        return detail_data

    def save_data(self, item):
        self.collection.find_one_and_update(
            {'id': item['id']},
            {'$set': item},
            upsert=True
        )


if __name__ == '__main__':
    shixin = Shixin()
    name = ['李飞']
    # proxy = shixin.get_proxy_available()
    # captcha = shixin.get_captcha(proxy=proxy)
    for name in name:
        page = pages = 1
        while True:
            res = shixin.request(name=name, page=page) # 获取列表页
            if res:
                pages, ids = shixin.parse_data(res)
                pages = int(pages)
                print('抓取进度： {}/{}，当前页用户： {}'.format(page, pages, ids))
                if ids:
                    shixin.proxy = get_proxy_available()
                    for id in ids:
                        detail_res = shixin.request(user_id=id) # 获取详情页
                        if detail_res:
                            item = shixin.parse_detail_data(detail_res)
                            print(item)
                            if item:
                                shixin.save_data(item)
                        # time.sleep(random.random()*5)
            page += 1
            if page == pages:
                break