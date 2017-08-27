#_*_ coding:utf-8 _*_

import requests
from bs4 import BeautifulSoup
import sys
sys.path.append('..')
from tools.db_operator import DataOperator


class ExpoChina:
    def __init__(self, sid, current_date, start_date, end_date):
        self.current_date = current_date
        self.sid = sid
        self.start_date = start_date
        self.end_date = end_date

    def get_data(self, url):
        header = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Encoding': 'gzip, deflate, sdch',
            'Accept-Language': 'zh-CN,zh;q=0.8',
            'Connection': 'keep-alive',
            'Cache-Control': 'max-age=0',
            'Host': 'www.expo-china.com',
            'Referer': 'https://www.expedia.cn/Hotel-Search?',
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.75 Safari/537.36'
        }
        try:
            data = requests.get(url, headers=header, timeout=5)
        except Exception as e:
            print('error:', e)
            return None
        else:
            if data.ok:
                return data.text
            else:
                print '网页出现错误！'
                return None

    def get_items(self, city_name, city_code,  page='1' ):
        url = 'http://www.expo-china.com/web/exhi/exhi_search.aspx?City=%s&Industry=-1&Start=%sT%s&page=%s'%(city_code, self.start_date, self.end_date, page)
        print '正在抓取%s第%s页的数据'%(city_name, page), url
        data = self.get_data(url)
        if data:
            soup = BeautifulSoup(data)
            items = []
            try:
                meetings=soup.findAll('div',{'class':'Resueltlist'})[0].findAll('li')
            except Exception as e:
                print('未找到展会数据，error：', e)
                return
            for meeting in meetings:
                item = {'sid':self.sid, 'begin_date':' ', 'end_date':' ', 'id':' ' , 'title':' ', 'industry':' ', 'city':city_name, 'venue':' ', 'organizer':' ', 'site':' ', 'visitor':' ', 'area':' ', 'history_info_tag':'0'}
                title = meeting.select('div')[0].h3.a.string.strip()
                href = meeting.select('div')[0].h3.a['href']
                id = href.split('-')[-1].split('.')[0]
                begin_date = meeting.select('div')[1].span.string.strip()
                print title, href, id, begin_date
                item['title'] = title
                item['id'] = id
                item['href'] = href
                item['begin_date'] = begin_date
                each_meeting_url = href
                each_meeting_data = self.get_data(each_meeting_url)
                if each_meeting_data:
                    each_meeting_soup = BeautifulSoup(each_meeting_data)
                    try:
                        each_meeting_info = each_meeting_soup.findAll('div', {'div','zhanhuijieshao_c'})[0]
                    except IndexError:
                        print '未找到%s的具体信息'%title
                        item['end_date'] = begin_date
                    else:
                        print '找到%s的具体信息'%title
                        try:
                            end_date = each_meeting_info.select('ul')[0].select('li')[0].text.split(u'至')[-1]
                        except IndexError:
                            end_date = begin_date
                        item['end_date'] = end_date
                        try:
                            venue = each_meeting_info.select('ul')[0].select('li')[1].text.split(u'：')[-1]
                        except IndexError:
                            venue = ' '
                        item['venue'] = venue
                        try:
                            organizer = each_meeting_info.select('div[class*="zhuban_danwei_big"]')[0].div.text.split(u'：')[-1].strip()
                        except IndexError:
                            organizer = ' '
                        item['organizer'] = organizer
                        print end_date, venue, organizer
                else:
                    print '未找到%s的详细数据'%title
                    item['end_date'] = begin_date
                    #item['venue'] = ' '
                    #item['organizer'] = ' '
                items.append(item)
            print '%s第%s页抓取完毕，准备写入'%(city_name, page)
            opera = DataOperator()
            opera.item_insert(data=items)
            try:
                next_url = soup.select('div[id="ctl00_MainPageHolder_webPage"]')[0].select('a')[-2]['href']
            except KeyError:
                print '全部抓取完毕!'
                return
            else:
                next_page = next_url.split('=')[-1]
                print '找到%s第%s页的数据'%(city_name, next_page)
                self.get_items(city_name, city_code, next_page)
        else:
            print('未找到第{}页的数据'.format(page))

if __name__ == '__main__':
    city_list = {
        '北京' : '1101',
        '上海' : '3101',
        '天津' : '1201',
        '重庆' : '5001',
        '深圳' : '4403',
        '广州' : '4401',
        #'东莞' : '',
        '南京' : '3201',
        '杭州' : '3301',
        #'宁波' : '3302',
        #'温州' : '3303',
        #'义乌' : '3307',
        '济南' : '3701',
        '青岛' : '3702',
        '成都' : '5101',
        '武汉' : '4201',
        '苏州' : '3202',
        '郑州' : '4101',
        '西安' : '6101',
        '海南' : '4600',        #包括海口和三亚
        '贵阳' : '5201',
        '昆明' : '5301',
        #'南昌' : '3601',
        '大连' : '2102',
        '沈阳' : '2101',
        '厦门' : '3502',
        '福州' : '3501',
        #'南宁' : '4501',
        #'长沙' : '4301'
    }
    current_date = '201601'
    sid = '21'
    start_date =  current_date[:4]+'-'+current_date[-2:]+'-'+'01'
    end_date = '2018-12-31'
    expo_china = ExpoChina(sid, current_date, start_date, end_date)
    for city_name, city_code in city_list.iteritems():
        data = expo_china.get_items(city_name, city_code)
