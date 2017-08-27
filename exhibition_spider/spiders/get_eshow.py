#_*_ coding:utf-8 _*_
import re
import requests
from bs4 import BeautifulSoup
import sys
sys.path.append('..')
import datetime
from tools.db_operator import DataOperator

class Eshow:
    def __init__(self, sid, current_date, start_date, end_date):
        self.current_date = current_date
        self.sid = sid
        self.start_date = start_date
        self.end_date = end_date

    def get_html(self, url, page=1, *city_id):
        if city_id:
            data = {'1':'1', 'tag':'0', city_id[0]:city_id[1], 'starttime':self.start_date, 'endtime':self.end_date, 'page':page}
            try:
                response = requests.post(url, data=data)
            except Exception as e:
                print('error:', e)
                return None
        else:
            try:
                response = requests.get(url)
            except Exception as e:
                print('error:', e)
                return None
        html = response.content
        return html

    def get_data(self, data):
        pattern_items = re.compile('<div.*?class="sslist">.*?<a.*?href="(.*?)".*?>(.*?)</a>.*?<p>(.*?)</p>.*?<p.*?class="cg">(.*?)</p>', re.S)
        meetings = re.findall(pattern_items, data)
        items = []
        items_history = []
        for meeting in meetings:
            item = {'sid':self.sid, 'begin_date':' ', 'end_date':' ', 'id':' ' , 'title':' ', 'industry':' ', 'city':' ', 'venue':' ', 'organizer':' ', 'site':' ', 'visitor':' ', 'area':' ', 'history_info_tag':'0'}
            print meeting[0]
            id = meeting[0].split('/')[-1].split('_')[0]
            print id
            item['id'] = id
            title= meeting[1].strip()
            item['title'] = title
            city = meeting[2].strip()
            item['city'] = city
            try:
                venue = meeting[3].split('>')[1].split('<')[0]
            except IndexError:
                venue = meeting[3].strip()
            item['venue'] = venue
            h = 'http://www.eshow365.com'+meeting[0]
            print h
            html2 = self.get_html(h)
            pattern_time = re.compile('举办时间：(.*?)---(.*?)</p>',re.S)
            pattern_organizer = re.compile('主办单位：(.*?)</p>')
            pattern_industry = re.compile('所属行业：(.*?)</a>')
            pattern_area = re.compile('展会面积：(\d+).*?</p>')
            time_tmp = re.findall(pattern_time, html2)
            begin_time_tmp = time_tmp[0][0].replace('/', '-')
            begin_date = datetime.datetime.strptime(begin_time_tmp,'%Y-%m-%d').strftime('%Y-%m-%d')
            end_time_tmp = time_tmp[0][1].replace('/', '-')
            end_date = datetime.datetime.strptime(end_time_tmp,'%Y-%m-%d').strftime('%Y-%m-%d')
            item['begin_date'] = begin_date
            item['end_date'] = end_date
            try:
                org = re.findall(pattern_organizer, html2)[0].split(' ')[0]
            except IndexError:
                org = ' '
            item['organizer'] = org
            industry_tmp = re.findall(pattern_industry, html2)
            if industry_tmp:
                try:
                    indus = industry_tmp[0].split('>')[1].split('<')[0]
                except IndexError:
                    indus = industry_tmp[0].strip()
            else:
                indus = ' '
            print indus
            item['industry'] = indus
            try:
                area = re.findall(pattern_area, html2)[0]
            except IndexError:
                area = ' '
            item['area'] = area

            soup = BeautifulSoup(html2)
            try:
                history_exhibitions = soup.findAll('div', {'class':'ljzh'})[0].select('tr')[1:]
            except IndexError:
                print '没有找到历届展会信息'
                history_info_tag = '0'
            else:
                print '找到历届展会信息'
                history_info_tag = '1'
                for history_exhibition in history_exhibitions:
                    item_history = {}
                    history_exhibition_info = history_exhibition.select('td')
                    history_exhibition_title = history_exhibition_info[0].a['title'].strip()
                    print history_exhibition_title
                    history_exhibition_url = history_exhibition_info[0].a['href']
                    history_exhibition_id = history_exhibition_url.split('/')[-1].split('_')[0]
                    print history_exhibition_id
                    try:
                        history_exhibition_venue = history_exhibition_info[1].stripped_strings.next()
                    except StopIteration:
                        history_exhibition_venue = ' '
                    print history_exhibition_venue
                    history_exhibition_date = history_exhibition_info[2].string.strip().replace('/', '-')
                    print history_exhibition_date
                    history_exhibition_area_tmp = history_exhibition_info[3].span.string.strip()
                    history_exhibition_area = filter(lambda x:x.isdigit(), history_exhibition_area_tmp)
                    print history_exhibition_area
                    item_history['sid'] = self.sid
                    item_history['itemid'] = id
                    item_history['history_itemid'] = history_exhibition_id
                    item_history['title'] = history_exhibition_title
                    item_history['venue'] = history_exhibition_venue
                    date_tmp = history_exhibition_date
                    date = datetime.datetime.strptime(date_tmp,'%Y-%m-%d').strftime('%Y-%m-%d')
                    item_history['date'] = date
                    item_history['area'] = history_exhibition_area
                    items_history.append(item_history)
            item['history_info_tag'] = history_info_tag
            items.append(item)
        opera = DataOperator()
        opera.item_insert(data=items, data_history=items_history)
        return

if __name__ == '__main__':
    current_date = '201608'
    start_date =  current_date[:4]+'/'+current_date[-2:]+'/'+'01'
    end_date = '2016/12/31'
    history_table_name='eventlist_info_history'
    sid = '13'
    url = 'http://www.eshow365.com/ZhanHui/Ajax/AjaxSearcherV3.aspx'
    city_list = {
        '北京' : ['areano', '1'],
        '天津' : ['areano', '2'],
        '上海' : ['areano', '9'],
        '江苏' : ['areano', '10'],
        '浙江' : ['areano', '11'],
        '广东' : ['areano', '19'],
        '重庆' : ['areano', '22'],
        '广西' : ['areano', '20'] ,        #海南
        '海南' : ['areano', '21'] ,        #海南
        '合肥' : ['Drpcity', '98'],
        '成都' : ['Drpcity', '235'],
        '济南' : ['Drpcity', '135'],
        '青岛' : ['Drpcity', '136'],
        '沈阳' : ['Drpcity', '37'],
        '大连' : ['Drpcity', '38'],
        '哈尔滨' : ['Drpcity', '60'],
        '郑州' : ['Drpcity', '152'],
        '长沙' : ['Drpcity', '183'],
        '武汉' : ['Drpcity', '169'],
        '贵阳' : ['Drpcity', '256'],
        '昆明' : ['Drpcity', '265'],
        '福州' : ['Drpcity', '115'],
        '厦门' : ['Drpcity', '116'],
        '南昌' : ['Drpcity', '124'],
        '西安' : ['Drpcity', '288'],
    }
    eshow = Eshow(sid, current_date, start_date, end_date)
    for city_name, city_info in city_list.items():
        pages = 1
        for page in range(1, pages+1):
            print('正在爬取%s第%s页'%(city_name, page))
            html = eshow.get_html(url, page, *city_info)
            if html:
                if page == 1:
                    pattern_pages = re.compile('<option.*?value="1".*?selected=.*?>1/(\d+).*?</option>')
                    pages = re.findall(pattern_pages, html)[0]
                    print '%s共%s页'%(city_name, pages)
                eshow.get_data(html)