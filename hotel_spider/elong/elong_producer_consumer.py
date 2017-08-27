#coding:utf-8
import requests
import time
import random
import math
import datetime
from elong.db import hotel_basic_info
from elong.db import hotel_detail_info
from threading import Thread
from queue import Queue
from bs4 import BeautifulSoup

queue = Queue()
error_id = []

def print_run_time(func):
    """装饰器函数，输出运行时间"""
    def wrapper(*args, **kw):
        start_time = time.time()
        func()
        print('run time is {:.2f}'.format(time.time() - start_time))
    return wrapper


class SaveBasicInfo(Thread):

    '''请求页面'''
    def down_page(self, page=1, **city_info):
        headers = {
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'zh-CN,zh;q=0.8',
            'Connection': 'keep-alive',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'Host': 'hotel.elong.com',
            'Origin': 'http://hotel.elong.com',
            'Referer': 'http://hotel.elong.com',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36',
            'X-Requested-With': 'XMLHttpRequest'
        }
        data = {
            'listRequest.checkInDate': str(check_in),
            'listRequest.checkOutDate': str(check_out),
            'listRequest.cityID': city_info['city_id'],
            'listRequest.cityName': city_info['city_name'],
            'listRequest.pageIndex': page,
            'listRequest.pageSize': '20',
        }
        response = requests.post('http://hotel.elong.com/ajax/list/asyncsearch', headers=headers, data=data)
        return response.json()

    '''从列表页获取酒店的基本信息'''
    def save_hotels_basic_info(self, **city_info):
        response = self.down_page(**city_info)  #先请求一次，获取酒店总数量和页数
        hotel_count = response['value']['hotelCount']
        pages = int(math.ceil(int(hotel_count)/20.0))
        print('{}在{}～{}期间共有{}家酒店，共{}页'.format(city_info['city_name'], str(check_in), str(check_out), hotel_count, pages))
        for page in range(1, pages+1):
            print('正在爬取第{}页'.format(page))
            response = self.down_page(page=page, **city_info)
            ids = response['value']['hotelIds']
            # print(ids)
            # print(hotels_info)
            global queue
            for id in ids.split(','):
                queue.put(id)
            print('产生:', ids)
            time.sleep(random.random())
            hotels_info = response['value']['hotelListHtml']
            soup = BeautifulSoup(hotels_info)
            hotels = soup.findAll('div', {'class': 'h_item'})
            # print(len(hotels))
            for hotel in hotels:
                hotel_id = hotel['data-hotelid']
                # hotel_name = basic_info.find('span',{'class':'l1'})['data-hotelname']
                hotel_name = hotel.find('p',{'class':'h_info_b1'}).a['title'].strip()
                # hotel_address = basic_info.find('span',{'class':'l1'})['data-hoteladdress']
                hotel_address = hotel.find('p', {'class':'h_info_b2'}).text.split(']')[-1].strip() #去除商圈信息
                try:
                    hotel_lng = hotel.find('span',{'class':'l1'})['data-lng']
                except Exception as e:
                    hotel_lng = ''
                try:
                    hotel_lat = hotel.find('span',{'class':'l1'})['data-lat']
                except Exception as e:
                    hotel_lat = ''
                hotel_lowest_price = hotel.find('span', {'class':'h_pri_num'}).text
                try:
                    hotel_review_rate = hotel.find('span', {'method':'review'}).i.text
                except Exception as e:
                    hotel_review_rate = ''
                try:
                    hotel_review_num = hotel.find('span', {'class':'c555 block mt5'}).b.text
                except Exception as e:
                    hotel_review_num = ''
                # print(hotel_id,hotel_name,hotel_address,hotel_lng,hotel_lat,hotel_lowest_price,hotel_review_rate,hotel_review_num)
                basic_info = {
                    'id': hotel_id,
                    'name': hotel_name,
                    'address': hotel_address,
                    'lng': hotel_lng,
                    'lat': hotel_lat,
                    'lowest_price': hotel_lowest_price,
                    'review_rate': hotel_review_rate,
                    'review_num': hotel_review_num
                }
                hotel_basic_info.insert_one(basic_info)

    def run(self):
        city_list = [
            # {'city_id': '0101', 'city_name':'北京'},
            # {'city_id': '0201', 'city_name':'上海'},
            # {'city_id': '2001', 'city_name':'广州'},
            # {'city_id': '2003', 'city_name':'深圳'},
            # {'city_id': '1201', 'city_name':'杭州'},
            # {'city_id': '1801', 'city_name':'武汉'},
            # {'city_id': '1702', 'city_name':'洛阳'},
            # {'city_id': '2601', 'city_name':'拉萨'},
            {'city_id': '1720', 'city_name':'信阳'}
        ]
        for city in city_list:
            print(city)
            self.save_hotels_basic_info(**city)


class SaveDetailInfo(Thread):

    def down_page(self, hotel_id=''):
        headers = {
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'zh-CN,zh;q=0.8',
            'Connection': 'keep-alive',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'Host': 'hotel.elong.com',
            'Origin': 'http://hotel.elong.com',
            'Referer': 'http://hotel.elong.com',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36',
            'X-Requested-With': 'XMLHttpRequest'
        }
        if hotel_id:
            data = {
                'detailRequest.hotelIDs': hotel_id,
                'detailRequest.checkInDate': str(check_in),
                'detailRequest.checkOutDate': str(check_out)
            }
            headers['Referer'] = 'http://hotel.elong.com/{}/'.format(hotel_id)
            response = requests.post('http://hotel.elong.com/ajax/detail/gethotelroomsetjva', headers=headers, data=data)
            if response.json()['success']:
                data = response.json()['value']['content']
                if data:
                    return data
                else:
                    error_id.append(hotel_id)
                    return None

    '''从详情页获取酒店的详细信息'''
    def save_hotel_detail_info(self, hotel_id):
        rooms_info = self.down_page(hotel_id=hotel_id)
        if rooms_info:
            soup = BeautifulSoup(rooms_info, 'lxml')
            print(soup.prettify())
            rooms = soup.findAll('div',{'class':'htype_item'})
            for room in rooms:
                room_id = room['data-roomid']
                try:
                    room_lowest_price = room.find('span',{'class':'htype_info_num'}).text   #房间最低价
                except Exception:
                    room_lowest_price = ''
                room_name = room.find('p',{'class':'htype_info_name'}).text     #房间名
                room_area = room.find('p',{'class':'htype_info_ty'}).select('span')[0].text.lstrip('房间').rstrip('㎡')
                # room_area = re.sub('[^0-9]+', '', room_area)
                try:
                    room_bed_type = room.find('p',{'class':'htype_info_ty'}).select('span')[2].text     #床型
                except Exception:
                    room_bed_type = ''
                try:
                    room_check_in_num = room.find('span',{'class':'vm'}).text.strip()
                except Exception:
                    try:
                        room_check_in_num = len(room.find('p',{'class':'htype_info_ty'}).select('span')[4].select('i')) #入住人数
                    except Exception:
                        room_check_in_num = ''
                sub_rooms = room.tbody.select('tr[data-handle="rp"]')
                for sub_room in sub_rooms:
                    sub_room_name = sub_room.select('td[class="ht_name"]')[0].span.text.strip()     #子房间名，即产品名
                    sub_room_supply = sub_room.select('td[class="ht_supply"]')[0].text.strip()      #供应商
                    try:
                        sub_room_discount = sub_room.select('i[class="icon_dis_w1"]')[0].text.strip()
                    except Exception:
                        sub_room_discount = ''
                    try:
                        sub_room_breakfast = sub_room.select('td[class="ht_brak"]')[0].text.strip()     #早餐
                    except Exception:
                        sub_room_breakfast = ''
                    try:
                        sub_room_cancel_rule = sub_room.select('td[class="ht_rule"]')[0].text.strip()   #取消规则
                    except Exception:
                        sub_room_cancel_rule = ''
                    try:
                        sub_room_price_cost = sub_room.select('span[class="ht_pri_cost"]')[0].text.strip()    #成本价
                    except Exception:
                        sub_room_price_cost = ''
                    try:
                        sub_room_price_avg = sub_room.select('span[class="ht_pri_num"]')[0].text.strip()      #日均价
                    except Exception:
                        sub_room_price_avg = ''
                    if not sub_room_price_avg:
                        sub_room_price_avg = ''     #待处理
                    if sub_room.find('i',{'class':'icon_yufu'}):  #如果有这个标签
                        sub_room_prepay = '预付,为了保障您的预订，需要您预先在网上支付房费，到店后直接办理入住~'
                    else:
                        sub_room_prepay = ''
                    if sub_room.find('i',{'class':'icon_danbao'}):  #如果有这个标签
                        sub_room_guarantee = '担保,房型太抢手了，酒店需要您提供信用卡或支付宝担保预订'
                    else:
                        sub_room_guarantee = ''
                    if sub_room.find('i', {'class':'icon_li'}):   #如果有这个标签
                        sub_room_gift = '礼'
                    else:
                        sub_room_gift = ''
                    if sub_room.find('i', {'class':'icon_comit'}):   #如果有这个标签
                        sub_room_confirm_timely = '立即确认,此产品为立即确认系列，订单提交后，酒店将立即确认您的订单，保障您的住房需求'
                    else:
                        sub_room_confirm_timely = ''
                    if sub_room.find('i', {'class':'icon_qiang'}):   #如果有这个标签
                        sub_room_qiang = '抢,此产品正在参加限时抢购，低折扣！ 限时抢！'
                    else:
                        sub_room_qiang = ''
                    try:
                        # sub_room_return = sub_room.select('span[class="h_pri_fan"]')[0].text.strip()        #返现
                        sub_room_return = sub_room.select('td[class="ht_retu"]')[0].text.strip().rstrip('元')
                    except Exception:
                        sub_room_return = ''
                    sub_room_booking_status = sub_room.select('td[class="ht_book"]')[0].text.strip().replace('\n', ' ') #预订状态
                    if not sub_room_booking_status:
                        if sub_room.find('i',{'class':'icon_phone_excl'}):
                            sub_room_booking_status = '手机专享'
                        if sub_room.find('i',{'class':'icon_yufu_d5'}):
                            sub_room_booking_status = 'APP新用户专享，折扣优惠'
                    detail_info = {
                        'hotel_id': hotel_id,
                        'sub_room_name': sub_room_name,
                        'sub_room_supply': sub_room_supply,
                        'sub_room_discount': sub_room_discount,
                        'sub_room_gift': sub_room_gift,
                        'sub_room_confirm_timely': sub_room_confirm_timely,
                        'sub_room_qiang': sub_room_qiang,
                        'sub_room_breakfast': sub_room_breakfast,
                        'sub_room_cancel_rule': sub_room_cancel_rule,
                        'sub_room_price_cost': sub_room_price_cost,
                        'sub_room_price_avg': sub_room_price_avg,
                        'sub_room_return': sub_room_return,
                        'sub_room_booking_status': sub_room_booking_status,
                        'sub_room_prepay': sub_room_prepay,
                        'sub_room_guarantee': sub_room_guarantee,
                        'room_id': room_id,
                        'room_name': room_name,
                        'room_lowest_price': room_lowest_price,
                        'room_area': room_area,
                        'room_bed_type': room_bed_type,
                        'room_check_in_num': room_check_in_num,
                    }
                    print(detail_info)
                    hotel_detail_info.insert_one(detail_info)

    def run(self):
        global queue
        while not queue.empty():
            hotel_id = queue.get()
            queue.task_done()
            print('取出',hotel_id)
            time.sleep(random.random())
            self.save_hotel_detail_info(hotel_id)

@print_run_time
def start():
    producers, consumers = [], []
    for i in range(1):
        p = SaveBasicInfo()
        producers.append(p)
        p.start()
    time.sleep(3)       #避免consumer线程启动后，队列为空
    for i in range(4):
        s = SaveDetailInfo()
        consumers.append(s)
        s.start()

    for i in producers:
        i.join()
    for i in consumers:
        i.join()


if __name__ == '__main__':
    check_in = datetime.date.today()
    check_out = check_in + datetime.timedelta(days=1)
    # start()
    SaveDetailInfo().save_hotel_detail_info('41101001')