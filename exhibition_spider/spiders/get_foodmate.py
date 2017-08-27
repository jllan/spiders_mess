#_*_ coding:utf-8 _*_
import re
import requests
from bs4 import BeautifulSoup
import sys
sys.path.append('..')
from tools.db_operator import DataOperator


class FoodMate:

    def __init__(self, sid, current_date):
        self.current_date = current_date
        self.sid = sid

    def get_data(self, url):
        print url
        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Encoding': 'gzip, deflate, sdch',
            'Accept-Language': 'zh-CN,zh;q=0.8',
            'Connection': 'keep-alive',
            'Host': 'www.foodmate.net',
            'Upgrade-Insecure-Requests' :1,
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.94 Safari/537.36'
        }
        result = requests.get(url, headers=headers)
        data = result.text
        return data

    def get_items(self, start_date, page='1'):
        url = 'http://www.foodmate.net/exhibit/search.php?kw=&fields=0&fromdate=%s&todate=&catid=0&process=0&order=0&x=59&y=12&page=%s'%(start_date, page)
        data = self.get_data(url)
        soup = BeautifulSoup(data)
        meetings = soup.findAll('div', {'class':'list'})
        print meetings
        items = []
        if meetings:
            for meeting in meetings:
                item = {'sid':self.sid, 'begin_date':' ', 'end_date':' ', 'id':' ' , 'title':' ', 'industry':' ', 'city':' ', 'venue':' ', 'organizer':' ', 'site':' ', 'visitor':' ', 'area':' ', 'history_info_tag':'0'}
                meeting = meeting.ul
                href = meeting.select('li')[0].a['href']
                itemid = href.split('-')[-1].split('.')[0]
                title = meeting.select('li')[0].a.string
                venue_tmp = meeting.select('li')[1].string
                venue = venue_tmp.split(':')[-1]
                organizer_tmp = meeting.select('li')[2].string
                organizer = organizer_tmp.split(':')[-1]
                date_tmp = meeting.select('li')[3].string
                begin_date = date_tmp.split('~')[0].strip()
                end_date = date_tmp.split('~')[1].strip()
                each_meeting_url = href
                each_meeting_data = self.get_data(each_meeting_url)
                pattern_city = re.compile(u'展出城市.*?<a.*?>(.*?)</a>', re.S)
                pattern_site = re.compile(u'<div.*?id="content">.*?网址.*?<a.*?>(.*?)</a>.*?<br>', re.S)
                try:
                    city = re.findall(pattern_city, each_meeting_data)[0]
                except IndexError:
                    city = ' '
                try:
                    site = re.findall(pattern_site, each_meeting_data)[0]
                except IndexError:
                    site = ' '
                print itemid, title, city, begin_date, end_date, organizer, venue, site
                item['id'] = itemid
                item['title'] = title
                item['city'] = city
                item['venue'] = venue
                item['begin_date'] = begin_date
                item['end_date'] = end_date
                item['organizer'] = organizer
                item['site'] = site
                items.append(item)
            opera = DataOperator()
            opera.item_insert(data=items)
            pattern_next_page = re.compile(u'<a.*?href=".*?page=(\d+)"\s+title="下一页">')
            try:
                next_page = re.findall(pattern_next_page, data)[0]
            except IndexError:
                print '全部抓取完毕'
                return
            else:
                print '找到下一页，准备抓取下一页的数据'
                self.get_items(start_date, next_page)

if __name__ == '__main__':
    current_date = '201608'
    sid = '32'
    start_date = current_date+'01'
    food_mate = FoodMate(sid, current_date)
    food_mate.get_items(start_date)
