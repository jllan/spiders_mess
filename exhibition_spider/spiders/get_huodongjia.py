#_*_ coding:utf-8 _*_

import requests, json
import time
from tqdm import *
import sys
sys.path.append('..')
from tools.db_operator import DataOperator

class HuoDongJia:

    def __init__(self, sid, current_date):
        self.url = 'http://m.huodongjia.com'
        self.current_date = current_date
        self.sid = sid
        self.s = requests.session()

    def get_data(self, page='', id=''):
        header = {
                    'Accept': '*/*',
                    'Accept-Encoding': 'gzip, deflate, sdch',
                    'Accept-Language': 'zh-CN,zh;q=0.8',
                    'Connection': 'keep-alive',
                    'Host': 'm.huodongjia.com',
                    'Referer': 'http://m.huodongjia.com/business/',
                    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.75 Safari/537.36'
                }
        if id:
            url = self.url + '/event-%s.html'%id
        else:
            header['X-Requested-With'] = 'XMLHttpRequest'
            url = self.url + '/business/page-%s/?json=1'%page
        print url
        response = self.s.get(url, headers = header)
        print(response.text)
        if response.status_code == 403:     #访问被禁止
            return None
        else:
            data = response.content
            return data

    def getItems(self, page):
        data = self.get_data(page=page)
        data = json.loads(data)
        if data:
            print '找到第%s页的数据' %page
            meetings = data['events']
            items = []
            if meetings:
                for meeting in meetings:
                    if not meeting:
                        print '全部爬取完毕'
                        break
                    item = {'sid':self.sid, 'begin_date':' ', 'end_date':' ', 'id':' ' , 'title':' ', 'industry':' ', 'city':' ', 'venue':' ', 'organizer':' ', 'site':' ', 'visitor':' ', 'area':' ', 'history_info_tag':'0'}
                    itemid = meeting['event_id']
                    title = meeting['event_name']
                    begin_date = meeting['event_begin_time'][:10]
                    print itemid, title
                    if ''.join(begin_date.split('-')[:2]) >= self.current_date:
                        end_date = meeting['event_end_time'][:10]
                        try:
                            city = meeting['event_city_info'][0]['district_name']
                        except IndexError:
                            city = ''
                        try:
                            venue = meeting['event_venue_info'][0].get('title')
                        except IndexError:
                            venue = city
                        visitor = meeting.get('event_scale', ' ')
                        if not visitor:
                            visitor = ''
                        try:
                            organizer = meeting['event_sponsor'][0].get('ns_name', '')
                        except IndexError:
                            organizer = ''
                        print itemid, title, city, venue, begin_date ,end_date, visitor, organizer
                        item['id'] = itemid
                        item['title'] = title
                        item['city'] = city
                        item['venue'] = venue
                        item['begin_date'] = begin_date
                        item['end_date'] = end_date
                        item['visitor'] = visitor
                        items.append(item)
                    else:
                        print '第%s页ID为%s的数据过期'%(page, itemid)
                opera = DataOperator()
                opera.item_insert(data=items)
                return
            else:
                print '第%s页没有展会数据' %page
                return
        else:
            print '访问到%s页时被禁止，暂停6分钟后继续!'%(page)
            for i in tqdm(range(3600)):
                time.sleep(.1)
                self.getItems(page)


if __name__ == '__main__':
    current_date = '201608'
    sid = '31'
    huodongjia = HuoDongJia(sid, current_date)
    pages = range(1, 100)   #爬取前100页的数据
    start = time.time()
    for page in pages:
        huodongjia.getItems(page)
    print 'huodongjia持续时间:', time.time()-start