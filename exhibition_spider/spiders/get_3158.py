#_*_ coding:utf-8 _*_
import requests
import re
from bs4 import BeautifulSoup
import sys
sys.path.append('..')
from tools.db_operator import DataOperator


class Get3158:
    def __init__(self, current_date, sid):
        self.current_date = current_date
        self.sid = sid

    def get_html(self, url):
        try:
            response = requests.get(url)
        except Exception as e:
            print('error:', e)
            return None
        html = response.text
        return html

    # 获取总页数
    def get_pages(self, url):
        html = self.get_html(url)
        pattern_pages = re.compile('<a\shref.*?/(\d+)/.*?>尾页</a>')
        pages = re.findall(pattern_pages, html)
        if pages:
            return int(pages[0])
        else:
            soup = BeautifulSoup(html)
            href = soup.findAll('a', {'class' : 'pages'})
            pages = len(href) + 1
            return pages

    def get_data(self, page, city_name):
        pattern=re.compile('<dd>.*?<a.*?(\d+).html".*?>(.*?)</a>.*?<p>.*?<a.*?>(.*?)</a>.*?<i.*?>(.*?)</i>.*?<p>.*?<a.*?>(.*?)</a>.*?<a.*?>(.*?)</a>.*?</dd>', re.S)
        items = []
        url = 'http://zhanhui.3158.cn/zhxx/all/trade/%s/%s/'%(city_name, str(page))
        print('正在抓取第%s页的数据'%page)
        print(url)
        html = self.get_html(url)
        if html:
            data = re.findall(pattern, html)
            for i in data:
                item = {'begin_date':' ', 'end_date':' ', 'id':' ' , 'title':' ', 'industry':' ', 'city':' ', 'venue':' ', 'organizer':' ', 'site':' ', 'visitor':' ', 'area':' ', 'history_info_tag':'0'}
                begin_date = i[3].split(' ')[0]
                end_date = i[3].split(' ')[-1]
                year = int(begin_date.split('-')[0])
                month = int(begin_date.split('-')[1])
                if year >= int(self.current_date[:4])+1 or year == int(self.current_date[:4]) and month >= int(self.current_date[-2:]):
                    item['sid'] = self.sid
                    item['begin_date'] = begin_date
                    item['end_date'] = end_date
                    id = i[0]
                    item['id'] = id
                    title = i[1]
                    print(title)
                    item['title'] = title
                    industry = i[2]
                    item['industry'] = industry
                    city = i[4]
                    item['city'] = city
                    venue = i[5]
                    item['venue'] = venue
                    h2 = 'http://zhanhui.3158.cn/zhxx/n%s.html'%i[0]
                    print(h2)
                    html2 = self.get_html(h2)
                    pattern_organizer = re.compile('主办单位：(.*?)</span>',re.S)
                    organizer_tmp1 = re.findall(pattern_organizer, html2)
                    if organizer_tmp1:
                        try:
                            organizer_tmp2 = organizer_tmp1[0].split('>')[1].split('<')[0]
                        except IndexError:
                            org = re.split('、|\s', organizer_tmp1[0].strip())[0]
                        else:
                            org = re.split('、|\s', organizer_tmp2)[0]
                    else:
                        org = ' '
                    print(org)
                    item['organizer'] = org
                    items.append(item)
            if items:
                print('准备写入第%s页的数据'%page)
                opera = DataOperator()
                opera.item_insert(data=items)
            else:
                print('第%s页的数据全部过期，不会写入！'%page)
        else:
            print('未找到%s第%s页的数据'%(city_name, page))

if __name__ == '__main__':
    current_date = '201608'
    sid = '10'
    city_list = ['beijing', 'shanghai', 'guangzhou', 'shenzhen', 'tianjin', 'chongqing', 'chengdu', 'hangzhou', 'zhengzhou', 'jinan', 'qingdao', 'wuhan', 'xian', 'nanjing', 'hainan', 'suzhou', 'xiamen', 'dalian', 'shenyang', 'guiyang', 'kunming', 'fuzhou', 'dongguan']
    get_3158 = Get3158(current_date, sid)
    for city in  city_list:
        url = 'http://zhanhui.3158.cn/zhxx/all/trade/%s/'%city
        print(city, url)
        pages = get_3158.get_pages(url)
        print('%s共%s页'%(city, pages))
        for page in range(1, pages+1):
            get_3158.get_data(page, city)
        print('%s的数据全部抓取并写入完毕'%city)