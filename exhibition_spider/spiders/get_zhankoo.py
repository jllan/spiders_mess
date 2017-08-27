#_*_coding:utf-8 _*_

import requests
import re
from bs4 import BeautifulSoup
import sys
sys.path.append('..')
from tools.db_operator import DataOperator


class Zhankoo:
    def __init__(self, sid, current_date):
        self.current_date = current_date
        self.sid = sid

    def get_data(self, url):
        print url
        result = requests.get(url)
        data = result.text
        return data

    def get_items(self, city, page='1'):
        url = 'http://www.zhankoo.com/Search/SearchExhibitionList?city=%s&classifyId=0&ratingOverAll=0&rankType=5&isExhibitionEnd=0&_=1452759283208&pagenumber=%s'%(city, page)
        print '正在抓取%s第%s页的数据'%(city, page)
        data = self.get_data(url)
        soup = BeautifulSoup(data)
        meetings = soup.findAll('h3', {'class':'deal-tile__title'})
        items = []
        if meetings:
            for meeting in meetings:
                item = {'sid':self.sid, 'begin_date':' ', 'end_date':' ', 'id':' ' , 'title':' ', 'industry':' ', 'city':' ', 'venue':' ', 'organizer':' ', 'site':' ', 'visitor':' ', 'area':' ', 'history_info_tag':'0'}
                title = meeting.select('span[class="xtitle"]')[0].a['title']
                href = meeting.select('span[class="xtitle"]')[0].a['href']
                itemid = href.split('_')[-1].split('.')[0]
                date_venue_tmp = meeting.select('span[class="short-title"]')[0].text
                date_venue = ''.join(date_venue_tmp.split()[:-1])
                venue = date_venue.split('：')[-1]
                date_tmp = date_venue.split('：')[1]
                date = re.split(u"[\u4e00-\u9fa5]+",date_tmp)
                begin_date = date[0]
                end_date = date[1]
                print city, title, itemid, begin_date, end_date, venue
                item['id'] = itemid
                item['title'] = title
                item['city'] = city
                item['venue'] = venue
                item['begin_date'] = begin_date
                item['end_date'] = end_date
                items.append(item)
            opera = DataOperator()
            opera.item_insert(data=items)
            pattern_next_page = re.compile(u'<a\s+class="next-page".*?href=".*?pagenumber=(\d+)">下一页</a>')
            try:
                next_page = re.findall(pattern_next_page, data)[0]
            except IndexError:
                print '%s的数据全部抓取完毕'%city
                return
            else:
                print '找到%s的下一页，准备抓取下一页的数据'%city
                self.get_items(city,  next_page)
        else:
            print '%s没有数据'%city

if __name__ == '__main__':
    current_date = '201608'
    sid = '34'
    city_list = {
        '北京', '上海', '广东', '天津', '重庆', '江苏', '四川', '河南', '山东', '湖北', '陕西', '浙江','福建','辽宁', '贵州', '云南'
    }
    zhankoo = Zhankoo(sid, current_date)
    for city in city_list:
        zhankoo.get_items(city)


