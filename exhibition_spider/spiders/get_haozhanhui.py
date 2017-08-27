#_*_ coding:utf-8 _*_

import requests
import HTMLParser
import re
from bs4 import BeautifulSoup
import sys
sys.path.append('..')
from tools.db_operator import DataOperator


class Haozhanhui:
    def __init__(self, sid, current_date):
        self.current_date = current_date
        self.sid = sid

    def get_data(self, url):
        try:
            response = requests.get(url)
        except Exception,e:
            print 'error:',e
            return None
        else:
            # html = response.read().decode('utf-8')
            html = response.content
            html_parser = HTMLParser.HTMLParser()
            data = html_parser.unescape(html)
            return data

    def get_items(self, data):
        soup = BeautifulSoup(data)
        meetings_tmp = soup.findAll('ul', {'class':'trade-news haiwai'})[:2]
        for tmp in meetings_tmp:
            items = []
            items_history = []
            meetings = tmp.findAll('li')
            for meeting in meetings:
                item = {'sid':self.sid, 'begin_date':' ', 'end_date':' ', 'id':' ' , 'title':' ', 'industry':' ', 'city':' ', 'venue':' ', 'organizer':' ', 'site':' ', 'visitor':' ', 'area':' ', 'history_info_tag':' '}
                base_info = meeting.text.split()
                url = meeting.a['href']
                item['url'] = url
                id = url.split('_')[-1].split('.')[0]
                item['id'] = id
                begin_date = base_info[0]
                item['begin_date'] = begin_date
                item['end_date'] = begin_date
                industry = base_info[1].strip('】').strip('【')
                item['industry'] = industry
                city = base_info[2].strip('】').strip('【')
                item['city'] = city
                title = meeting.a['title']
                item['title'] = title
                print url, begin_date, industry, city, title
                each_meeting_url = url
                each_meeting_data = self.get_data(each_meeting_url)
                if each_meeting_data:
                    pattern_venue=re.compile(u'<ul>.*?展会场馆.*?<a.*?>(.*?)</a>', re.S)
                    pattern_organizer=re.compile(u'<ul>.*?组织单位.*?<a.*?>(.*?)</a>', re.S)
                    pattern_site=re.compile(u'<ul>.*?官方网站.*?</strong>(.*?)</li>', re.S)
                    pattern_area=re.compile(u'<ul>.*?约.*?(\d+).*?平米.*?</li>', re.S)
                    try:
                        venue = re.findall(pattern_venue, each_meeting_data)[0]
                    except IndexError:
                        venue = ' '
                    item['venue'] = venue
                    try:
                        organizer = re.findall(pattern_organizer, each_meeting_data)[0]
                    except IndexError:
                        organizer = ' '
                    item['organizer'] = organizer
                    try:
                        site = re.findall(pattern_site, each_meeting_data)[0]
                    except IndexError:
                        site = ' '
                    item['site'] = site
                    try:
                        area = re.findall(pattern_area, each_meeting_data)[0]
                    except IndexError:
                        area = ' '
                    item['area'] = area
                    print venue, organizer, site, area

                    soup = BeautifulSoup(each_meeting_data)
                    try:
                        history_exhibitions = soup.findAll('table', {'class':'tbsty exhtbl'})[0].select('tr')[1:]
                    except IndexError:
                        print '没有找到历届展会信息'
                        history_info_tag = '0'
                    else:
                        print '找到历届展会信息'
                        history_info_tag = '1'
                        for history_exhibition in history_exhibitions:
                            item_history = {}
                            history_exhibition_info = history_exhibition.select('td')[1:4]
                            history_exhibition_title = history_exhibition_info[0].a['title'].strip()
                            history_exhibition_url = history_exhibition_info[0].a['href']
                            history_exhibition_id = history_exhibition_url.split('_')[-1].split('.')[0]
                            history_exhibition_date = history_exhibition_info[0].a.string
                            print history_exhibition_title, history_exhibition_date, history_exhibition_url
                            history_exhibition_venue = history_exhibition_info[1].a['title'].strip()
                            print history_exhibition_venue
                            history_exhibition_area_tmp = history_exhibition_info[2].string.strip()
                            history_exhibition_area = filter(lambda x:x.isdigit(), history_exhibition_area_tmp)
                            print history_exhibition_area
                            item_history['sid'] = self.sid
                            item_history['itemid'] = id
                            item_history['history_itemid'] = history_exhibition_id
                            item_history['title'] = history_exhibition_title
                            item_history['venue'] = history_exhibition_venue
                            item_history['date'] = history_exhibition_date
                            item_history['area'] = history_exhibition_area
                            items_history.append(item_history)
                    item['history_info_tag'] = history_info_tag
                items.append(item)
            opera = DataOperator()
            opera.item_insert(data=items, data_history=items_history)

if __name__ == '__main__':
    current_date = '201608'
    sid = '20'
    url = 'http://www.haozhanhui.com/zhanlanjihua/'
    haozhanhui = Haozhanhui(sid, current_date)
    data = haozhanhui.get_data(url)
    haozhanhui.get_items(data)


