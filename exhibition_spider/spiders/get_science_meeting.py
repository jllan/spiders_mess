# _*_ coding:utf-8 _*_
import urllib
import urllib2
import re
from bs4 import BeautifulSoup
import sys
sys.path.append('..')
from tools.db_operator import DataOperator

class ScienceMeeting:
    def __init__(self, sid, current_date):
        self.current_date = current_date
        self.sid = sid

    def get_data(self, page):
        url = 'http://www.meeting.edu.cn/meeting/meeting/notice/meetingAction!getResult1.action'
        data = {'pageBean.currentPage':str(page), 'timeNo':'1'}
        postdata = urllib.urlencode(data)
        try:
            response = urllib2.urlopen(url, postdata)
        except Exception, e:
            print 'error:', e
            return None
        data = response.read()
        return data

    def get_items(self):
        try:
            data = self.get_data(1)
            soup = BeautifulSoup(data)
            pages = int(soup.pagecount.string)
        except Exception as e:
            print('error:', e)
            return None
        print '共%s页'%pages
        for page in range(1, pages+1):
            items = []
            print '正在抓取第%s页的数据'%page
            data = self.get_data(page)
            if data:
                soup = BeautifulSoup(data)
                meetings = soup.findAll('meeting')
                print '当前为第%s页'%soup.pageno
                for meeting in meetings:
                    item = {'sid':self.sid, 'begin_date':' ', 'end_date':' ', 'id':' ' , 'title':' ', 'industry':' ', 'city':' ', 'venue':' ', 'organizer':' ', 'site':' ', 'visitor':' ', 'area':' ', 'history_info_tag':'0'}
                    id = meeting.meetingid.string
                    item['id'] = id
                    item['title'] = meeting.meetingtitle.string
                    begin_date = meeting.meetingtime.string
                    item['begin_date'] = begin_date
                    city = meeting.meetingaddress.string
                    item['city'] = city
                    if meeting.subject.string:
                        item['industry'] = meeting.subject.string
                    each_meeting_url = 'http://www.meeting.edu.cn/meeting/meeting/notice/meetingAction-%s!detail.action'%id
                    print each_meeting_url
                    try:
                        each_meeting_data = urllib2.urlopen(each_meeting_url).read()
                    except Exception, e:
                        print 'error:', e
                    else:
                        pattern = re.compile('开始日期.*?<td.*?>(.*?)</td>.*?结束日期.*?<td.*?>(.*?)</td>.*?具体地点.*?<td.*?>(.*?)</td>.*?主办单位.*?<td.*?>(.*?)</td>.*?会议网站.*?<td.*?>.*?<a.*?>(.*?)</a>',re.S)
                        each_meeting_item = re.findall(pattern, each_meeting_data)[0]
                        print each_meeting_item
                        end_date = each_meeting_item[1].strip()
                        print end_date
                        if not end_date:
                            end_date = begin_date
                        item['end_date'] = end_date
                        location = each_meeting_item[2].strip()
                        print location
                        if not location:
                            location = city
                        item['venue'] = location
                        organizer = each_meeting_item[3].strip()
                        print organizer
                        item['organizer'] = organizer
                        site = each_meeting_item[4].strip()
                        item['site'] = site
                        print site
                    items.append(item)
                    print item
                print '第%s页抓取完毕'%page
                print '准备写入第%s页的数据'%page
                opera = DataOperator()
                opera.item_insert(data=items)
            else:
                print '未找到第%s页的数据'%page
        return

if __name__ == '__main__':
    current_date = '201608'
    sid = '19'
    science_meeting = ScienceMeeting(sid, current_date)
    items = science_meeting.get_items()