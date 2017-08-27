#_*_coding:utf-8 _*_

import re
import requests
import datetime
from bs4 import BeautifulSoup
import sys
sys.path.append('..')
from tools.db_operator import DataOperator

class ExpoWindow:

    def __init__(self, sid, current_date):
        self.url = 'http://www.expowindow.com/'
        self.current_date = current_date
        self.sid = sid

    def get_html(self, page='1', id='', cate=''):
        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Encoding': 'gzip, deflate, sdch',
            'Accept-Language': 'zh-CN,zh;q=0.8',
            'Connection': 'keep-alive',
            'Host': 'www.expowindow.com',
            #'Referer': 'http://www.expowindow.com/zhanhui/',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.94 Safari/537.36'
        }
        if id:
            headers['Referer'] = self.url + '/zhanhui/class_%s.html'%cate
            url = self.url + 'zhanhui/show_%s.html'%(id)
        else:
            print '正在查找类别为%s的第%s页的数据'%(cate, page)
            headers['Referer'] = self.url + '/zhanhui/'
            url = self.url + 'zhanhui/class_%s_%s.html'%(cate, page)
        print(url)
        try:
            response = requests.get(url, headers = headers)
            data = response.content.decode('gb18030', 'ignore')
        except Exception as e:
            print('error:', e)
            return None
        return data

    def get_items(self, cate, page='1'):
        try:
            data = self.get_html(page = page, cate = str(cate))
            soup = BeautifulSoup(data)
            events = soup.find('ul', {'id':'listul'}).select('li')
        except Exception as e:
            print('error:', e)
            return
        items = []
        for event in events:
            item = {'sid':self.sid, 'begin_date':' ', 'end_date':' ', 'id':' ' , 'title':' ', 'industry':' ', 'city':' ', 'venue':' ', 'organizer':' ', 'site':' ', 'visitor':' ', 'area':' ', 'history_info_tag':'0'}
            url = event.a['href']
            id = re.findall('\d+', url)[0]
            title = event.select('a[target="_blank"]')[0].text.strip()
            try:
                eachData = self.get_html(id=id)
                pattern_city=re.compile(u'>> 国内 >>(.*?)>>')
                city=re.findall(pattern_city, eachData)[0]
            except Exception, e:   #国外城市
                print 'error:', e
                continue
            else:
                eachSoup = BeautifulSoup(eachData)
                date_temp = eachSoup.select('span[class="dico2"]')[0].text.strip()
                date = re.split(u"[\u4e00-\u9fa5]+", date_temp)
                begin_date_temp = date[0]
                try:
                    begin_date = datetime.datetime.strptime(begin_date_temp,'%Y-%m-%d').strftime('%Y-%m-%d')
                except Exception,e:
                    print '未找到开始日期',e
                    begin_date = ''
                current_date_format = self.current_date[:4]+'-'+self.current_date[4:]
                if begin_date >= current_date_format:
                    end_date_temp = date[1]
                    end_date = datetime.datetime.strptime(end_date_temp,'%Y-%m-%d').strftime('%Y-%m-%d')
                    venue = eachSoup.select('span[class="dico2"]')[1].text
                    item['city'] = city
                    item['begin_date'] = begin_date
                    item['end_date'] = end_date
                    item['id'] = id
                    item['title'] = title
                    item['venue'] = venue
                    items.append(item)
                    print id,title,city,begin_date,end_date,venue
                else:
                    print 'id为%s的数据已过期'%id
        opera = DataOperator()
        opera.item_insert(data=items)
        pattern_nextPage = re.compile(u'<a href="/zhanhui/class_\d+_(\d+).html">下一页')
        try:
            next_page = re.findall(pattern_nextPage, data)[0]
        except IndexError,e:
            print '查找完毕'
        else:
            print '找到第%s页'%next_page
            self.get_items(cate=cate, page=next_page)


if __name__ == '__main__':
    current_date = '201608'
    sid = '36'
    expowindow = ExpoWindow(sid, current_date)
    category = range(1, 21)     #有20个分类
    for cate in category:
        print '正在查找类别%s的数据'%cate
        items = expowindow.get_items(cate=str(cate))