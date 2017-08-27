#_*_ coding:utf-8 _*_
import requests
import re
import math
from bs4 import BeautifulSoup
import sys
sys.path.append('..')
from tools.db_operator import DataOperator


class Huiyi77:
    def __init__(self, sid, current_date):
        self.current_date = current_date
        self.sid = sid

    def get_data(self, url):
        try:
            response = requests.get(url)
        except Exception as e:
            print('error:', e)
            return None
        data = response.text
        return data

    def get_items(self, begin_time):
        category = {'行业交流':'conferlist', '商业展会':'exhibition', '文艺赛事':'literature', '活动聚会':'event'}
        for key, value in category.iteritems():
            print '正在爬取%s的数据'%key
            first_url = 'http://www.77huiyi.com/meet/%s/?mc=&msi=%s&msa=&page=%s'%(value, begin_time, '1')
            print first_url
            try:
                data = self.get_data(first_url)
                pattern_numbers = re.compile(u'共(\d+)条')
                numbers = int(re.findall(pattern_numbers, data)[0])
                pages = int(math.ceil(numbers/20.0))
            except Exception as e:
                print('error:', e)
                continue
            if pages == 0:
                print('在%s下没找到数据'%key)
                continue
            else:
                print('在%s下有%s条数据,共%s页'%(key, numbers, pages))
            for page in range(1, int(pages)+1):
                items = []
                url = 'http://www.77huiyi.com/meet/%s/?mc=&msi=%s&msa=&page=%s'%(value, begin_time, page)
                print '正在爬取第%s页的数据'%page
                print url
                data = self.get_data(url)
                if not data:
                    print('未找到第%s页的数据'%page)
                    continue
                soup = BeautifulSoup(data)          #data显示正常，但是soup是乱码，暂时还没解决此问题
                meetings = soup.findAll('ul', {'class':'clearfix'})[1].findAll('li')
                for meeting in meetings:
                    item = {'sid':self.sid, 'begin_date':' ', 'end_date':' ', 'id':' ' , 'title':' ', 'industry':' ', 'city':' ', 'venue':' ', 'organizer':' ', 'site':' ', 'visitor':' ', 'area':' ', 'history_info_tag':'0'}
                    meeting_info=meeting.p
                    url=meeting_info.a['href']
                    id = url.split('/')[-2]
                    item['id'] = id
                    item['url'] = url
                    title=meeting_info.a.string
                    item['title'] = title
                    begin_date=meeting_info.select('span')[1].select('i')[0].string
                    item['begin_date'] = begin_date
                    city_tmp = meeting_info.select('span')[1].select('i')[1].string
                    try:
                        city = city_tmp.split()[-1]
                    except IndexError:
                        city = city_tmp
                    item['city'] = city
                    print url, title, begin_date, city
                    each_meeting_url =url
                    # each_meeting_data = urllib2.urlopen(each_meeting_url).read().decode('utf-8', 'ignore')
                    try:
                        each_meeting_data = requests.get(each_meeting_url).text
                        each_meeting_soup = BeautifulSoup(each_meeting_data)
                        each_meeting_info = each_meeting_soup.select('div[class*="conference-info"]')[0]
                    except Exception as e:
                        print('未找到%s的具体信息:%s'%(id, e))
                        item['end_date'] = begin_date
                    else:
                        end_date = each_meeting_info.select('span')[1].text.split('～')[-1].split()[0]
                        item['end_date'] = end_date
                        loc = each_meeting_info.select('span')[2].text.split()[-1]
                        item['venue'] = loc
                        print end_date, loc
                    items.append(item)
                opera = DataOperator()
                opera.item_insert(data=items)
        return

if __name__ == '__main__':
    current_date = '201608'
    sid = '19'
    begin_time = current_date[:4]+'-'+current_date[-2:]+'-'+'01'
    huiyi77 = Huiyi77(sid, current_date)
    huiyi77.get_items(begin_time)