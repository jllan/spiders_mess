#_*_coding:utf-8 _*_

import re
import requests
import HTMLParser
from bs4 import BeautifulSoup
import sys
sys.path.append('..')
from tools.db_operator import DataOperator

class Fairso:

    def __init__(self, sid, current_date):
        self.url = 'http://www.fairso.com'
        self.current_date = current_date
        self.sid = sid

    def get_html(self, page=1, id=''):
        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Encoding': 'gzip, deflate, sdch',
            'Accept-Language': 'zh-CN,zh;q=0.8',
            'Connection': 'keep-alive',
            'Host': 'www.fairso.com',
            'Referer': 'http://www.fairso.com/zhanhui/0-201700-6-1',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.94 Safari/537.36',
        }
        if id:
            url = self.url + '/fair/%s'%(id)
        else:
            url = self.url + '/zhanhui/0-000000-6-1/p/%s.html'%page   # 0-000000-6-1 表示国内展会，并且排在前边的是未开展的展会
        print url
        response = requests.get(url, headers = headers)
        html = response.text
        parser = HTMLParser.HTMLParser()
        data = parser.unescape(html)
        return data

    def get_items(self, page=1):
        data = self.get_html(page = page)
        numbers = re.findall('<div class="newFind">.*?(\d+).*?</div>', data)[0]
        # pages = math.ceil(float(numbers)/20)
        pages = 150     # 爬前150页的数据，后边的基本已过期
        for page in range(1, int(pages)+1):
            print '共有%s页%s条数据，目前正在抓取第%s页的数据'%(pages, numbers, page)
            data = self.get_html(page = page)
            soup = BeautifulSoup(data)
            events = soup.findAll('div', {'class':'mlm1r'})
            items = []
            for event in events:
                item = {'sid':self.sid, 'begin_date':' ', 'end_date':' ', 'id':' ' , 'title':' ', 'industry':' ', 'city':' ', 'venue':' ', 'organizer':' ', 'site':' ', 'visitor':' ', 'area':' ', 'history_info_tag':'0'}
                href = event.a['href']
                id = href.split('/')[-1].strip()
                title = event.select('li')[0].text.strip()
                venue = event.select('li')[1].select('span')[1].text.strip()
                date = event.select('li')[1].select('span')[0].text.strip()
                begin_date = date.split('-')[0].replace('.', '-')
                end_date = date.split('-')[1].replace('.', '-')
                if ''.join(begin_date.split('-')[:2]) > self.current_date:
                    '''try:
                        city = ''.join(jieba.analyse.extract_tags(venue, allowPOS=['ns']))
                    except Exception as e:
                        print 'error:', e'''
                    eachData = self.get_html(id=id)
                    try:
                        city = re.findall(u'地址.*?<span>(.*?)</span>', eachData)[0].split()[-1].rstrip(u'市')
                    except IndexError as e:
                        print 'error:', e
                        city = ''
                    item['city'] = city
                    item['begin_date'] = begin_date
                    item['end_date'] = end_date
                    item['id'] = id
                    item['title'] = title
                    item['venue'] = venue
                    items.append(item)
                    print id,title,city,begin_date,end_date,venue
                else:
                    print 'ID为%s的数据过期'%id
            print '正在写入第%s页的数据'%(page)
            opera = DataOperator()
            opera.item_insert(data=items)

if __name__ == '__main__':
    current_date = '201608'
    sid = '38'
    current_month=int(current_date[-2:])
    fairso = Fairso(sid, current_date)
    items = fairso.get_items()