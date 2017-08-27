# _*_ coding:utf-8 _*_

import urllib2
from bs4 import BeautifulSoup
import datetime
import re
import sys
sys.path.append('..')
from tools.db_operator import DataOperator


class Chemsoc:
    def __init__(self, sid, current_date):
        self.current_date = current_date
        self.sid = sid

    def get_data(self, url):

        try:
            html = urllib2.urlopen(url)
            data = html.read().decode('gbk')
        except Exception as e:
            print('error:', e)
            return None
        return data

    def get_items(self, year, month):
        url = 'http://www.chemsoc.org.cn/Meeting/Home/search.asp?mingcheng=&province=&y=%s&m=%s'%(year, month)
        print url
        try:
            data = self.get_data(url)
            pattern_pages = re.compile(u'第\d+页.*?共(\d+)页')
            pages = re.findall(pattern_pages, data)[0]
        except Exception as e:
            print('未找打%s年%s月的数据，error:%s'%(year, month, e))
            return
        if not int(pages):
            print '%s年%s月没有数据'%(year, month)
        else:
            print '%s年%s月共有%s页的数据'%(year, month, pages)
            for page in range(1, int(pages)+1):
                items = []
                url = 'http://www.chemsoc.org.cn/Meeting/Home/search.asp?page=%s&mingcheng=&province=&y=%s&m=%s'%(page, year, month)
                print url
                try:
                    data = self.get_data(url)
                    soup = BeautifulSoup(data)
                    meetings = soup.findAll('table', {'class':'meetings'})[0].findAll('tr')[1:]
                except Exception as e:
                    print('未找打%s年%s月%s页的数据，error:%s'%(year, month, page, e))
                    continue
                for meeting in meetings:
                    item = {'sid':self.sid, 'begin_date':' ', 'end_date':' ', 'id':' ' , 'title':' ', 'industry':' ', 'city':' ', 'venue':' ', 'organizer':' ', 'site':' ', 'visitor':' ', 'area':' ', 'history_info_tag':'0'}
                    href = meeting.select('td')[0].a['href']
                    itemid = href.split('=')[-1]
                    title = meeting.select('td')[0].a['title']
                    city = meeting.select('td')[1].input['value']
                    meeting_time = meeting.select('td')[2].input['value']
                    begin_time_tmp = re.split(u'-|至', meeting_time)[0]
                    meeting_begin_time = re.sub(u'[年月日]', '-', begin_time_tmp).rstrip('-')
                    try:
                        end_time_tmp1 = re.split(u'-|至', meeting_time)[1]
                    except IndexError:
                        meeting_end_time = meeting_begin_time
                    else:
                        end_time_tmp2 = re.sub(u'[年月日]', '-', end_time_tmp1).rstrip('-')
                        if len(end_time_tmp2) <= 2:
                            if int(end_time_tmp2) < int(meeting_begin_time.split('-')[-1]):
                                meeting_end_time = meeting_begin_time.split('-')[0]+'-'+str(int(meeting_begin_time.split('-')[1])+1)+end_time_tmp2
                            else:
                                meeting_end_time = meeting_begin_time.replace(meeting_begin_time.split('-')[-1], end_time_tmp2)
                        elif len(end_time_tmp2) <= 4:
                            meeting_end_time = meeting_begin_time.split('-')[0] + '-' + end_time_tmp2
                    print itemid, city, title, meeting_begin_time, meeting_end_time
                    item['id'] = itemid
                    item['title'] = title
                    item['city'] = city
                    try:
                        begin_date = datetime.datetime.strptime(meeting_begin_time,'%Y-%m-%d').strftime('%Y-%m-%d')
                    except ValueError:
                        begin_date = meeting_begin_time
                    item['begin_date'] = begin_date
                    try:
                        end_date = datetime.datetime.strptime(meeting_end_time,'%Y-%m-%d').strftime('%Y-%m-%d')
                    except ValueError:
                        end_date = meeting_end_time
                    item['end_date'] = end_date
                    each_meeting_url = 'http://www.chemsoc.org.cn/Meeting/Home/'+href
                    print each_meeting_url
                    each_meeting_data = self.get_data(each_meeting_url)
                    if each_meeting_data:
                        pattern_organizer = re.compile(u'<p>主办单位：(.*?)</p>')
                        pattern_visitor = re.compile(u'<p>预计人数：(.*?)</p>')
                        pattern_venue = re.compile(u'<p>地.*?址：(.*?)</p>')
                        try:
                            organizer = re.findall(pattern_organizer, each_meeting_data)[0]
                        except IndexError:
                            organizer = ' '
                        try:
                            visitor = re.findall(pattern_visitor, each_meeting_data)[0]
                        except IndexError:
                            visitor = ' '
                        try:
                            venue = re.findall(pattern_venue, each_meeting_data)[0]
                        except IndexError:
                            venue = city
                        item['organizer'] = organizer
                        item['visitor'] = visitor
                        item['venue'] = venue
                    items.append(item)
                opera = DataOperator()
                opera.item_insert(data=items)
        return


if __name__ == '__main__':
    current_date = '201608'
    sid = '30'
    chemsoc = Chemsoc(sid, current_date)
    for month in range(int(current_date[-2:]), 13):
        chemsoc.get_items(current_date[:4], str(month))
    chemsoc.get_items(str(int(current_date[:4])+1), '')
