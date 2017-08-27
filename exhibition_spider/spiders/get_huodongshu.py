#_*_coding:utf-8 _*_
import requests
import time
from bs4 import BeautifulSoup
import jieba.analyse
import sys
sys.path.append('..')
from tools.db_operator import DataOperator

class HuoDongShu:

    def __init__(self, sid, current_date):
        self.url = 'http://www.huodongshu.com'
        self.current_date = current_date
        self.sid = sid

    def get_html(self, page, month):
        headers = {
            'Accept': '*/*',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'zh-CN,zh;q=0.8',
            'Connection': 'keep-alive',
            'Host': 'www.huodongshu.com',
            'Origin': 'http://www.huodongshu.com',
            'Referer': 'http://www.huodongshu.com/html/find.html',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.94 Safari/537.36',
            'X-Requested-With': 'XMLHttpRequest'
        }
        params = {
            'count': '10',
            'type':'1',
            'category_one': '222',
            'category_two': 'all',
            'city_name': '222',
            'time_can': month+3,
            'page': page
        }
        url = self.url + '/event/getComEventListPcData.do'
        print url
        response = requests.post(url, headers = headers, params = params)
        data = response.json()
        if data['msg'] == 'ok':
            return data['data']

    def get_items(self, month, page=1):
        data = self.get_html(page = page, month = month)
        pages, numbers = data['pageCount'], data['total']
        #print '%月份共有%s页%s条数据，目前正在抓取第%s页的数据'%(pages, numbers, page)
        for page in range(1, int(pages)+1):
            print '%s月份共有%s页%s条数据，目前正在抓取第%s页的数据'%(month, pages, numbers, page)
            data = self.get_html(page = page, month = month)
            events = data['list']
            items = []
            for event in events:
                item = {'sid':self.sid, 'begin_date':' ', 'end_date':' ', 'id':' ' , 'title':' ', 'industry':' ', 'city':' ', 'venue':' ', 'organizer':' ', 'site':' ', 'visitor':' ', 'area':' ', 'history_info_tag':'0'}
                id = event.get('id')
                title = event.get('name')
                venue = event.get('place')
                try:
                    city = event.get('city_name').rstrip('市')
                except Exception,e:
                    print 'error:',e
                    address = jieba.analyse.extract_tags(venue, allowPOS=['ns'])    #对展会场馆分词保留地名
                    if address:
                        city = address[0]
                    else:
                        city = ''

                begin_date = time.strftime('%Y-%m-%d', time.localtime(float(event.get('start_time'))))
                end_date = time.strftime('%Y-%m-%d', time.localtime(float(event.get('end_time'))))
                eachUrl = event.get('long_url')
                if eachUrl:
                    eachData = requests.get(eachUrl).content
                    try:
                        visitor = BeautifulSoup(eachData).find('span', {'data-id':'dimensions'}).text.rstrip('人')
                    except Exception,e:
                        print 'error:',e
                        visitor = ''
                item['city'] = city
                item['begin_date'] = begin_date
                item['end_date'] = end_date
                item['id'] = id
                item['title'] = title
                item['venue'] = venue
                item['visitor'] = visitor
                items.append(item)
                print id,title,city,begin_date,end_date,venue,visitor
            print '正在写入%s月份第%s页的数据'%(month, page)
            opera = DataOperator()
            opera.item_insert(data=items)




if __name__ == '__main__':
    current_date = '201608'
    sid = '37'
    current_month=int(current_date[-2:])
    huodongshu = HuoDongShu(sid, current_date)
    months = range(current_month, 13)     #按月份爬取
    for month in months:
        print '正在查找%s月份的数据'%month
        huodongshu.get_items(month = month)