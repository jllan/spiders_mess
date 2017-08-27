#_*_ coding:utf-8 _*_
import re
import requests
import sys
sys.path.append('..')
from tools.db_operator import DataOperator

class Cnean:
    def __init__(self, current_date, sid):
        self.current_date = current_date
        self.sid = sid

    def get_html(self, url, try_num=1):
        try:
            response = requests.get(url)
        except Exception as e:
            print('获取数据失败', e)
            return None
        else:
            html = response.text
            return html

    # 获取一个城市的总页数
    def get_pages(self, city_id):
        url = 'http://www.cnena.com/showroom/search.php?mid=1&fid=0&keyword=%s&action=search&type=title&page=1'%city_id
        print(url)
        html = self.get_html(url)
        pattern = re.compile('<a.*?href=".*?page=(\d+)"\stitle="尾页">')
        pages = re.findall(pattern, html)
        return pages[0]

    def get_data(self, page, city_name):
        items = []
        print('正在抓取%s第%s页的数据'%(city_name, page))
        url = 'http://www.cnena.com/showroom/search.php?mid=1&fid=0&keyword=%s&action=search&type=title&page=%s'%(city_name, str(page))
        url = url.decode('utf-8').encode('GBK')
        print(url)
        html = self.get_html(url)
        if html:
            pattern = re.compile('<tr>.*?<td.*?>(\d+)</td>.*?<a.*?href="(.*?)".*?>(.*?)</a>.*?<a.*?>(.*?)</a>.*?</tr>', re.S)
            meetings = re.findall(pattern, html)
            if meetings:
                for meeting in meetings:
                    item = {'sid':self.sid, 'begin_date':' ', 'end_date':' ', 'id':' ' , 'title':' ', 'industry':' ', 'city':city_name, 'venue':' ', 'organizer':' ', 'site':' ', 'visitor':' ', 'area':' ', 'history_info_tag':'0'}
                    fid_id_tmp = re.findall('\d+', meeting[1])
                    fid_id = str(fid_id_tmp[0]) + '-' + str(fid_id_tmp[1])
                    item['id'] = fid_id
                    title = meeting[2]
                    item['title'] = title
                    industry = meeting[3]
                    item['industry'] = industry
                    h = 'http://www.cnena.com/showroom/'+meeting[1]
                    print(h)
                    html2 = self.get_html(h)
                    if html2:
                        pattern2=re.compile(u'展会概况.*?开幕日期：(.*?)<br>.*?结束日期：(.*?)<br>.*?展会地点.*?<a.*?>(.*?)</a>',re.S)
                        meetings2 = re.search(pattern2, html2)
                        if meetings2:
                            print(meetings2.group(1))
                            begin_date = re.sub('\D+','-',meetings2.group(1)).strip('-')
                            end_date = re.sub('\D+','-',meetings2.group(2)).strip('-')
                            year = int(begin_date.split('-')[0])
                            month = int(begin_date.split('-')[1])
                            if year >= int(self.current_date[:4])+1 or year == int(self.current_date[:4]) and month >= int(self.current_date[-2:]):
                                item['begin_date'] = begin_date
                                item['end_date'] = end_date
                                venue = meetings2.group(3)
                                item['venue'] = venue
                                print(item)
                                items.append(item)
                print('准备写入第%s页的数据'%page)
                opera = DataOperator()
                opera.item_insert(data=items)
        else:
            print('%s页的数据为空'%page)
        return


if __name__ == '__main__':
    current_date = '201608'
    sid = '11'
    city_list = {
        '北京' : 3, '上海' : 8, '广州' : 3, '深圳' : 2, '天津' : 1, '重庆' : 1, '杭州' : 1, '成都' : 1,
        '郑州' : 1, '青岛' : 1, '济南' : 1, '武汉' : 1, '南京' : 1, '西安' : 1, '苏州' : 1, '福州' : 1,
        '厦门' : 1, '沈阳' : 1, '大连' : 1, '贵阳' : 1, '昆明' : 1, '东莞' : 1, '哈尔滨': 1, '长沙': 1,
        '南宁': 1,
        # '北海': 1,
    }
    cnean = Cnean(current_date, sid)
    for city_name, pages in city_list.iteritems():
        print('%s大约有%s页'%(city_name, pages))
        for page in range(1,int(pages)+1):
            cnean.get_data(page, city_name)