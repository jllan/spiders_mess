#_*_ coding:utf-8 _*_
import urllib2
import requests
import re
import time, datetime
import sys
sys.path.append('..')
from tools.db_operator import DataOperator

class Onezh:
    def __init__(self, sid, current_date):
        self.current_date = current_date
        self.sid = sid

    def get_html(self, city_id='1_0_0', page_id='1', begin_date='0', end_date='0'):
        url = 'http://www.onezh.com/zhanhui/'+page_id+'_'+city_id+'_'+begin_date+'/'+end_date+'/'
        print url
        try:
            response = requests.get(url)
            # html = response.read().decode('utf-8')
        except Exception as e:
            print('error:', e)
            return None
        html = response.text
        return html

    def get_items(self, city_name, city_id, begin_date, end_date):
        print u'准备爬取%s的数据'%(city_name)
        try:
            html = self.get_html(city_id, '1', begin_date, end_date)
            pages = re.findall(u'共(\d+)页', html)[0]
        except Exception as e:
            print('未找到%s的数据，error:%s' %(city_name, e))
            return
        print u'%s共%s页'%(city_name, pages)
        for page in range(1, int(pages)+1):
            items = []
            print u'正在爬取%s第%s页'%(city_name, page)
            try:
                html = self.get_html(city_id, str(page), begin_date, end_date)
                pattern = re.compile(u'div.*?class=\"info.*?<strong>.*?<a.*?href="(.*?)".*?>(.*?)</a>.*?<em.*?class="cgree1">.*?展会时间：(.*?)展馆：(.*?)</a>', re.S)
                meetings = re.findall(pattern, html)[0:]
            except Exception as e:
                print('未找到%s第%s页的数据，error:%s'%(city_name, page, e))
                continue
            for meeting in meetings:
                item = {'sid':self.sid, 'begin_date':' ', 'end_date':' ', 'id':' ' , 'title':' ', 'industry':' ', 'city':city_name, 'venue':' ', 'organizer':' ', 'site':' ', 'visitor':' ', 'area':' ', 'history_info_tag':'0'}
                id = meeting[0].split('_')[-1].split('.')[0]
                item['id'] = id
                title = meeting[1]
                item['title'] = title
                time_tmp = meeting[2]
                begin_time_tmp1 = time_tmp.split('---')[0]
                begin_time_tmp2 = re.sub(u'[年月日]', '-', begin_time_tmp1).rstrip('-')
                try:
                    begin_time = datetime.datetime.strptime(begin_time_tmp2,'%Y-%m-%d').strftime('%Y-%m-%d')
                except TypeError:
                    begin_time = begin_time_tmp2
                item['begin_date'] = begin_time
                end_time_tmp1 = time_tmp.split('---')[1].split('日')[0]
                end_time_tmp2 = re.sub(u'[年月日]', '-', end_time_tmp1)
                if len(end_time_tmp2) < 3:                                     #如果len(end_date_temp)=3，说明结束日期只有日期，没有年份和月份
                    end_time_tmp3 = begin_time.replace(begin_time.split('-')[-1], end_time_tmp2)     #把开始日期的日期数值换成结束日期的值
                elif len(end_time_tmp2) < 6:                                   #如果len(end_date_temp)=6,说明结束日期有月份和日期，没有年份
                    end_time_tmp3 = begin_time.split('-')[0] + '-' + end_time_tmp2   #把开始日期的年份数值与结束日期连接起来
                else:
                    end_time_tmp3 = end_time_tmp2
                try:
                    end_time = datetime.datetime.strptime(end_time_tmp3,'%Y-%m-%d').strftime('%Y-%m-%d')
                except TypeError:
                    end_time = end_time_tmp3
                item['end_date'] = end_time
                try:
                    venue = meeting[3].split('>')[-1]
                except IndexError:
                    venue = meeting[3]
                item['venue'] = venue
                time.sleep(2)
                try:
                    each_meeting_html = urllib2.urlopen('http://www.onezh.com'+meeting[0]).read().decode('utf-8')
                    pattern_area = re.compile(u'<div.*?class="title-detail">.*?<b>面积</b>.*?(\d+).*?</div>', re.S)
                    area = re.findall(pattern_area, each_meeting_html)[0]
                except Exception:
                    print('未找到面积数据')
                    area = ' '
                item['area'] = area
                pattern_industry = re.compile(u'<div.*?class="title-detail">.*?所属行业(.*?)</div>', re.S)
                try:
                    industry = re.findall(pattern_industry, each_meeting_html)[0].split('>')[-1]
                except IndexError:
                    industry = ' '
                item['industry'] = industry
                pattern_organizer = re.compile(u'<div.*?class="title-detail">.*?主办单位(.*?)</div>', re.S)
                try:
                    organizer = re.findall(pattern_organizer, each_meeting_html)[0].split('>')[-1]
                except IndexError:
                    organizer = ' '
                item['organizer'] = organizer
                pattern_site = re.compile(u'<li>.*?<b>网址(.*?)</li>', re.S)
                try:
                    site = re.findall(pattern_site, each_meeting_html)[0].split('>')[-1]
                except IndexError:
                    site = ' '
                item['site'] = site
                print id, title, begin_time, end_time, venue, industry, organizer
                items.append(item)
            opera = DataOperator()
            opera.item_insert(data=items)
        return

if __name__ == '__main__':
    city_list = {
        '北京': '1_0_0',
        '上海': '21_0_0',
        '广州': '423_424_0',
        '深圳': '423_524_0',
        '东莞': '423_441_0',
        '天津': '42_0_0',
        '南京': '1643_1644_0',
        '苏州': '1643_1692_0',
        '扬州': '1643_1748_0',
        '杭州': '3133_3134_0',
        #'宁波': '3133_3182_0',
        #'温州': '3133_3218_0',
        #'金华': '3133_3162_0',
        '济南': '2182_2183_0',
        '青岛': '2182_2268_0',
        '重庆': '62_0_0',
        '成都': '2589_2590_0',
        '武汉': '1320_1321_0',
        '郑州': '998_999_0',
        '西安': '2471_2472_0',
        '海南': '788_0_0',        #包括海口和三亚
        '贵阳': '690_691_0',
        '昆明': '2987_2988_0',
        '南昌': '1763_1764_0',
        '大连': '1874_1912_0',
        '沈阳': '1874_1875_0',
        '哈尔滨': '1176_1177_0',
        '厦门': '227_303_0',
        '福州': '227_228_0',
        '南宁': '566_567_0',
        '桂林': '566_617_0',
        '长沙': '1436_1437_0'
    }
    current_date = '201608'
    sid = '18'
    begin_date = current_date+'01'
    end_date = '20181231'
    onezh = Onezh( sid, current_date)
    for key, value in city_list.iteritems():
        onezh.get_items(key, value, begin_date, end_date)