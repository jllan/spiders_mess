#_*_ coding:utf-8 _*_

import urllib2
import urllib
import re
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
sys.path.append('..')
from tools.db_operator import DataOperator


class SciencenetMeeting:
    def __init__(self, sid, current_date):
        self.current_date = current_date
        self.sid = sid

    def get_data(self, begin_date, end_date, page, try_num=1):
        url = 'http://meeting.sciencenet.cn/index.php?s=/Category/search_result&p=%s'%page
        post_data = {
            'subword' : '输入关键字',
            'mttype' : '0',
            'mtcategory' : '0',
            'begintime' : begin_date,
            'endtime' : end_date,
            'type1' : 'news',
            'wzcategory' : '0'
        }
        postdata = urllib.urlencode(post_data)
        request = urllib2.Request(url, postdata)
        try:
            response = urllib2.urlopen(request, timeout=5)
        except Exception, e:
            print '第%s次获取失败:'%try_num, e
            if try_num<2:
                try_num += 1
                print '进行第%s次尝试'%try_num    #再次尝试获取数据
                self.get_data(begin_date, end_date, page, try_num)
            else:
                print '未找到数据！'
                return None     #如果两次都失败，就返回错误
        else:
            return response.read()

    def get_items(self, begin_date, end_date, page):
        data = self.get_data(begin_date, end_date, page)
        if data:
            pattern = re.compile(u'<tr>.*?<td.*?</td>.*?<td.*?<a.*?href="(.*?)".*?>(.*?)</a>.*?</td>.*?<td>.*?</td>.*?<td.*?>.*?<span.*?>(.*?)</span>.*?<td>.*?</td>.*?<td.*?>(.*?)</td>.*?</tr>', re.S)
            meetings = re.findall(pattern, data)
            items = []
            if meetings:
                for meeting in meetings:
                    item = {'sid':self.sid, 'begin_date':' ', 'end_date':' ', 'id':' ' , 'title':' ', 'industry':' ', 'city':' ', 'venue':' ', 'organizer':' ', 'site':' ', 'visitor':' ', 'area':' ', 'history_info_tag':'0'}
                    url = meeting[0].strip()
                    print url
                    id_tmp = url.split('=')[-1]
                    if len(id_tmp) > 10:            #id_tmp不是id，是网址
                        item['site'] = id_tmp       #url直接就是会议网址，没有id
                        id = ''
                    else:
                        id = id_tmp
                    print id
                    item['id'] = id
                    title = meeting[1].strip()
                    print title
                    item['title'] = title
                    city = meeting[2].strip()
                    print city
                    item['city'] = city
                    begin_time = meeting[3].strip()
                    print begin_time
                    item['begin_date'] = begin_time
                    if id:
                        if 'http' not in url:
                            url2 = 'http://meeting.sciencenet.cn'+url
                        else:
                            url2 = url
                        print url2
                        try:
                            data2 = urllib2.urlopen(url2).read() #根据每个会议的url，获取主办方起始日期等信息
                        except Exception, e:
                            print e
                            item['end_date'] = item['begin_date']
                            item['organizer'] = ' '
                            item['venue'] = city
                        else:
                            pattern_date = re.compile('会议时间.*?<td>(.*?)</td>')
                            pattern_venue = re.compile('会议地点.*?<td>(.*?)</td>')
                            pattern_organizer = re.compile('主办单位.*?<td>(.*?)</td>')
                            pattern_site = re.compile('官方网址.*?<td>.*?<a.*?href="(.*?)">.*?</a>.*?</td>')
                            try:
                                date = re.findall(pattern_date, data2)[0]
                            except IndexError:
                                item['end_date'] = begin_time
                            else:
                                item['end_date'] = date.split('至')[-1]
                            print item['end_date']
                            try:
                                organizer = re.findall(pattern_organizer, data2)[0]
                            except IndexError:
                                organizer = ' '
                            print organizer
                            item['organizer'] = organizer
                            try:
                                venue = re.findall(pattern_venue, data2)[0]
                            except IndexError:
                                venue = city
                            print venue
                            item['venue'] = venue
                            try:
                                site = re.findall(pattern_site, data2)[0]
                            except IndexError:
                                site = ' '
                            print site
                            item['site'] = site
                    else:
                        item['end_date'] = item['begin_date']
                        item['organizer'] = ' '
                        item['venue'] = city
                    items.append(item)
                opera = DataOperator()
                opera.item_insert(data=items)
        else:
            print '未找到第%s页的数据' %page
        try:
            next_url=re.findall(u'<a.*?href=\'(.*?)\'>下一页', data)[0]
        except IndexError:
            print "抓取完毕!"
            return
        else:
            print '找到下一页', next_url
            next_page = next_url.split('=')[-1]
            self.get_items(begin_date, end_date, next_page)

if __name__ == '__main__':
    current_date = '201608'
    sid = '19'
    begin_date  = current_date[:4]+'-'+current_date[-2:]+'-'+'01'
    end_date = '2018-12-31'
    sciencenet_meeting = SciencenetMeeting(sid, current_date)
    items = sciencenet_meeting.get_items(begin_date, end_date, '1')