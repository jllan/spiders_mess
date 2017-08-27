#_*_coding:utf-8 _*_

import re, time
import requests
from bs4 import BeautifulSoup
import sys
sys.path.append('..')
from tools.db_operator import DataOperator

class BanDengHui:

    def __init__(self, sid, current_date):
        self.url = 'http://www.bandenghui.com'
        self.current_date = current_date
        self.sid = sid

    def getData(self, page=int, id=''):
        header = {
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                    'Accept-Encoding': 'gzip, deflate, sdch',
                    'Accept-Language': 'zh-CN,zh;q=0.8',
                    'Connection': 'keep-alive',
                    'Host': 'www.bandenghui.com',
                    'Upgrade-Insecure-Requests': '1',
                    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/48.0.2564.109 Safari/537.36'
                }
        if id:
            url = self.url + '/meeting/%s.html'%id
        else:
            url = self.url + '/list/0-0-0-0-0-0.html?&page=%s' %page
        try:
            response = requests.get(url, headers=header)
        except Exception, e:
            print 'error:', e
            return None
        else:
            return response.content


    def getItems(self, page):
        page = page*20
        data = self.getData(page)
        if data:
            print u'成功获取第%s页的数据'%page
            soup = BeautifulSoup(data, 'lxml')
            meetings = soup.findAll('ul', {'class':'mod-meet-lt'})[0].findAll('li', recursive=False)
            items = []
            for meeting in meetings:
                item = {'sid':self.sid, 'begin_date':' ', 'end_date':' ', 'id':' ' , 'title':' ', 'industry':' ', 'city':' ', 'venue':' ', 'organizer':' ', 'site':' ', 'visitor':' ', 'area':' ', 'history_info_tag':'0'}
                meeting_url = meeting.a['href']
                meeting_id = meeting_url.split('/')[-1].split('.')[0]
                meeting_title = meeting.find('div',{'class':'mt-title'}).string.strip()
                meeting_city = meeting.find('span',{'class':'info-city'}).string.strip()
                meeting_time = meeting.find('span',{'class':'info-time'}).string.split()[0]
                print meeting_title, meeting_url, meeting_id, meeting_city
                each_meeting_data = self.getData(id=meeting_id)
                if each_meeting_data:
                    each_meeting_soup = BeautifulSoup(each_meeting_data, 'lxml')
                    try:
                        meeting_date = each_meeting_soup.find('li', {'title':u'活动时间'}).text.strip()
                    except AttributeError:
                        meeting_begin_date = meeting_end_date = meeting_time
                        #continue
                    else:
                        print meeting_date
                        meeting_begin_date = meeting_date.split('~')[0].split(' ')[0]
                        meeting_end_date = meeting_date.split('~')[-1].strip().split(' ')[0]
                        year = int(meeting_begin_date.split('-')[0])
                        month = int(meeting_begin_date.split('-')[1])
                        if year >= int(self.current_date[:4])+1 or year == int(self.current_date[:4]) and month >= int(self.current_date[-2:]):
                            try:
                                meeting_venue = each_meeting_soup.find('li', {'title':u'活动地点'}).text.strip().split()[0]
                            except AttributeError:
                                meeting_venue = ''
                            try:
                                meeting_visitors = each_meeting_soup.find('li', {'title':u'活动人数'}).text.strip().rstrip(u'人')
                            except AttributeError:
                                meeting_visitors = ''
                            try:
                                meeting_organizer = each_meeting_soup.find('li', {'title':u'主办单位'}).text.strip()
                            except AttributeError:
                                meeting_organizer = ''
                            print meeting_id, meeting_title, meeting_city, meeting_begin_date, meeting_end_date, meeting_venue, meeting_visitors, meeting_organizer
                            item['id'] = meeting_id
                            item['title'] = meeting_title
                            item['city'] = meeting_city
                            item['begin_date'] = meeting_begin_date
                            item['end_date'] = meeting_end_date
                            item['venue'] = meeting_venue
                            item['organizer'] = meeting_organizer
                            item['visitor'] = meeting_visitors
                            items.append(item)
                        else:
                            print u'id为%s的数据过期'%meeting_id
                else:
                    print '未找到id为%s的展会的其他数据'%meeting_id
            opera = DataOperator()
            opera.item_insert(data=items)
        else:
            print '未找到第%s页的数据'%page

if __name__ == '__main__':
    current_date = '201608'
    sid = '35'
    pages = range(50)   #当天之后的数据集中在前50页，本月当天之前的数据集中在后50页
    bandenghui = BanDengHui(sid, current_date)
    start = time.time()
    for page in pages:
        bandenghui.getItems(page)
    print 'huodongjia持续时间:', time.time()-start
