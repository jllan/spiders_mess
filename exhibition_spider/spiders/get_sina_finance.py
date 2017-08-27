#_*_ coding:utf-8 _*_
import urllib2
from bs4 import BeautifulSoup
import re
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
sys.path.append('..')
from tools.db_operator import DataOperator

"""
说明:
    网站名: 新浪财经
    地址: http://biz.finance.sina.com.cn/meeting/showAllMeeting.php
    包含信息: title, city, begin_date, end_date, site, organizer
    缺少信息: 场馆(默认venue=city), id(默认id=m190002)
"""

class SinaFinance:
    def __init__(self, sid, current_date):
        self.current_date = current_date
        self.sid = sid

    def get_data(self, year):
        url = 'http://biz.finance.sina.com.cn/meeting/showAllMeeting.php?year=%s'%year
        try:
            response = urllib2.urlopen(url)
            data = response.read().decode('gbk')
        except Exception as e:
            print('error:', e)
            return None
        return data

    def get_items(self, data, month):
        print('正在解析%s月份的数据'%month)
        soup = BeautifulSoup(data)
        meetings = soup.findAll('table', {'id':'tbl_%s'%month})[0].findAll('tr', {'class':'blue_bg'})
        items = []
        if meetings:
            for meeting in meetings:
                item = {'sid':self.sid, 'begin_date':' ', 'end_date':' ', 'id':'m190003' , 'title':' ', 'industry':'财经', 'city':' ', 'venue':' ', 'organizer':' ', 'site':' ', 'visitor':' ', 'area':' ', 'history_info_tag':'0'}
                url = meeting.select('td')[0].a['href']
                if url:
                    item['site'] = url
                title = meeting.select('td')[0].a.string
                if title:
                    item['title'] = title
                organizer = meeting.select('td')[1].string
                if organizer:
                    item['organizer'] = organizer
                date = meeting.select('td')[2].string
                if len(date) > 12:
                    begin_date_tmp = date.split('-')[0]
                    begin_date = re.sub('[^\d]', '-', begin_date_tmp).rstrip('-')
                    end_date_tmp = date.split('-')[1]
                    end_date_tmp2 = re.sub('[^\d]', '-', end_date_tmp).rstrip('-')
                    if len(end_date_tmp) <= 3:                                     #如果len(end_date_temp)=3，说明结束日期只有日期，没有年份和月份
                        end_date = begin_date.replace(begin_date.split('-')[-1], end_date_tmp2)     #把开始日期的日期数值换成结束日期的值
                    elif len(end_date_tmp) <= 6:                                   #如果len(end_date_temp)=6,说明结束日期有月份和日期，没有年份
                        end_date = begin_date.split('-')[0] + '-' + end_date_tmp2   #把开始日期的年份数值与结束日期连接起来
                    else:
                        end_date = end_date_tmp2
                else:
                    begin_date = end_date = re.sub('[^\d]', '-', date).rstrip('-')
                item['begin_date'] = begin_date
                item['end_date'] = end_date
                city = meeting.select('td')[3].string
                if city:
                    item['city'] = city
                    item['venue'] = city
                print(item)
                items.append(item)
            opera = DataOperator()
            opera.item_insert(data=items)
        else:
            print '%s年%s月没有数据!'%(self.current_date[:4], month)
        return items

if __name__ == '__main__':
    current_date = '201608'
    sid = '19'
    sina_finance = SinaFinance(sid, current_date)
    data = sina_finance.get_data('2016')
    if data:
        for month in range(int(current_date[-2:]), 13):
            items = sina_finance.get_items(data, month)