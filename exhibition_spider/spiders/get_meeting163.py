#_*_ coding:utf-8 _*_
import urllib2
import re
from bs4 import BeautifulSoup
import sys
sys.path.append('..')
import datetime
from tools.db_operator import DataOperator


"""
说明:
    网站名: 中国会议网
    地址: http://www.meeting163.com/meeting_type.asp?count=1
    包含信息: title, id, city, begin_date, end_date, location, site
    缺少信息: 主办方(默认organizer='')
"""


class Meeting163:
    def __init__(self, sid, current_date):
        self.current_date = current_date
        self.sid = sid

    def get_data(self, page):
        url = 'http://www.meeting163.com/meeting_type.asp?count=%s'%page
        try:
            response = urllib2.urlopen(url)
        except Exception as e:
            print('error:', e)
            return None
        data = response.read().decode('gbk')
        return data

    def get_items(self, page):
        print '正在抓取第%s页的数据'%page
        data = self.get_data(page).split('</html>')[1]
        if data:
            soup = BeautifulSoup(data)
            items = []
            meetings = soup.select('table[class="block1"] tr td tr')[1:]
            for meeting in meetings:
                item = {'sid':self.sid, 'begin_date':' ', 'end_date':' ', 'id':' ' , 'title':' ', 'industry':' ', 'city':' ', 'venue':' ', 'organizer':' ', 'site':' ', 'visitor':' ', 'area':' ', 'history_info_tag':'0'}
                date_tmp1 = meeting.select('td')[3].string
                date_tmp2 = re.sub(u'[年月日]', '-', date_tmp1).rstrip('-')
                print date_tmp2
                try:
                    date = datetime.datetime.strptime(date_tmp2,'%Y-%m-%d').strftime('%Y-%m-%d')
                except ValueError:
                    date = date_tmp2
                year = int(date.split('-')[0])
                month = int(date.split('-')[1])
                if year >= int(self.current_date[:4])+1 or year == int(self.current_date[:4]) and month >= int(self.current_date[-2:]):
                    id = meeting.select('td')[0].string
                    item['id'] = id
                    title = meeting.select('td')[1].a['title']
                    item['title'] = title
                    url = meeting.select('td')[1].a['href']
                    item['site'] = url
                    city = meeting.select('td')[2].string
                    item['city'] = city
                    data2 = urllib2.urlopen(url).read().decode('gbk')
                    pattern_date_loc = re.compile(u'召开时间.*?</span>(.*?)<br>.*?结束时间.*?</span>(.*?)<br>.*?地点.*?</span>(.*?)<br>', re.S)
                    date_loc = re.search(pattern_date_loc, data2)
                    if date_loc:
                        begin_date_tmp = date_loc.group(1).replace('.', '-')
                        try:
                            begin_date = datetime.datetime.strptime(begin_date_tmp,'%Y-%m-%d').strftime('%Y-%m-%d')
                        except ValueError:
                            begin_date = begin_date_tmp
                        item['begin_date'] = begin_date
                        end_date_tmp = date_loc.group(2).replace('.', '-')
                        try:
                            end_date = datetime.datetime.strptime(end_date_tmp,'%Y-%m-%d').strftime('%Y-%m-%d')
                        except ValueError:
                            end_date = end_date_tmp
                        item['end_date'] = end_date
                        loc = ''.join(date_loc.group(3).split())    #地点中有空格
                        item['venue'] = loc
                    else:
                        item['begin_date'] = item['end_date'] = date
                        item['venue'] = city
                    items.append(item)
            opera = DataOperator()
            opera.item_insert(data=items)
        else:
            print('未找到第%s页的数据'%page)

if __name__ == '__main__':
    current_date = '201608'
    sid = '19'
    meeting163 = Meeting163(sid, current_date)
    for page in range(1, 10):
        items = meeting163.get_items(page)        #抓取前十页的数据