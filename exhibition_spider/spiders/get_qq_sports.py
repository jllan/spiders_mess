# _*_ encoding:utf-8 _*_
import json
import StringIO
import urllib2
import gzip
import sys
sys.path.append('..')
from tools.db_operator import DataOperator

def get_data(url, id):
    header = {
        'Accept': '*/*',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
        'Connection': 'keep-alive',
        'Host': 'cgi.yanchu.qq.com',
        'Referer': 'http://y.qq.com/yanchu/category.html?type=4&city=0&page='+id+'&g_f=',
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; WOW64; rv:41.0) Gecko/20100101 Firefox/41.0'
    }
    try:
        request = urllib2.Request(url, headers = header)
        response = urllib2.urlopen(request)
        html = response.read()
        compressedData = StringIO.StringIO(html)
        decompressedDara = gzip.GzipFile(fileobj=compressedData)
        data = decompressedDara.read().encode('utf-8')
        data_use = data.lstrip('callback(').rstrip('\n;\)')
        data_dict = json.loads(data_use)
    except Exception as e:
        print('error:', e)
        return None
    return data_dict


def get_items(sid, current_date):
    items = []
    url = 'http://cgi.yanchu.qq.com/cgi-bin/yanchu/mb_api/jsondata.fcg?g_tk=4d3754f563ad04a56fece81bbcc83302&cbk=callback&sCmd=citytype&IDS=0%2C26&page=0&_=1446602940456'
    data = get_data(url,  str(1))
    if data and data['data']['page_data']:
        pages = int(data['data']['page_tol'])
        print '共%s页'%pages
        for page in range(pages):
            print page
            url = 'http://cgi.yanchu.qq.com/cgi-bin/yanchu/mb_api/jsondata.fcg?g_tk=4d3754f563ad04a56fece81bbcc83302&cbk=callback&sCmd=citytype&IDS=0%2C26&page='+str(page)+'&_=1446602940456'
            data = get_data(url, str(page+1))
            if not data or not data['data']['page_data']:
                print('未找到第%s页的数据'%page)
                continue
            print data
            for i in data['data']['page_data']:
                item = {'sid':sid, 'begin_date':' ', 'end_date':' ', 'id':' ' , 'title':' ', 'industry':' ', 'city':' ', 'venue':' ', 'organizer':' ', 'site':' ', 'visitor':' ', 'area':' ', 'history_info_tag':'0'}
                item['city'] = i['city']
                item['id'] = i['show_id']
                item['title'] = i['show_name']
                if len(i['show_time']) > 19:
                    begin_time = i['show_time'].split(',')[0].split(' ')[0]
                    end_time = i['show_time'].split(',')[-1].split(' ')[0]
                else:
                    begin_time = i['show_time'][:10]
                    end_time = begin_time
                item['begin_date'] = begin_time
                item['end_date'] = end_time
                item['venue'] = i['hall_name']
                items.append(item)
            opera = DataOperator()
            opera.item_insert(data=items)
        return items


if __name__ == '__main__':
    current_date = '201608'
    sid = '50'
    get_items(sid, current_date)

