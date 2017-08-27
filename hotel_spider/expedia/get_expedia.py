#_*_coding:utf-8 _*_

import re
import requests
import json
import time, datetime
from bs4 import BeautifulSoup
import MySQLdb
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

def getData(url, func='get', postData=None, try_num=1):
    print func
    header = {
                'Accept': '*/*',
                'Accept-Encoding': 'gzip, deflate',
                'Accept-Language': 'zh-CN,zh;q=0.8',
                'Connection': 'keep-alive',
                'Host': 'www.expedia.cn',
                'Referer': 'https://www.expedia.cn/Hotel-Search?',
                'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; WOW64; rv:41.0) Gecko/20100101 Firefox/41.0'
            }
    if func == 'post':
        try:
            response = requests.post(url, data=postData, headers=header)
        except Exception, e:
            print '第%s次获取失败:'%try_num, e
            if try_num<2:
                try_num += 1
                print '进行第%s次尝试'%try_num    #再次尝试获取数据
                getData(url, 'post', postData, try_num)
            else:
                return None     #如果两次都失败，就返回错误
        else:
            try:
                data_dict = json.loads(response.text)
            except Exception, e:        #如果获取到了数据，但是json转成字典时出错
                print '第%s次获取到的数据有误:'%try_num, e
                if try_num<2:
                    try_num += 1
                    print '进行第%s次尝试'%try_num    #再次尝试获取数据
                    getData(url, 'post', postData, try_num)
                else:
                    return None     #如果两次都失败，就返回错误
            else:
                return data_dict
            #return response.text

    if func == 'get':
        response = requests.get(url)
        if response.status_code == 200:
            return response.text
        else:
            print 'Error!'
            return None

def getItems(url, city, startDate, endDate, sort, page='1'):
    #url = 'https://www.expedia.cn/Hotel-Search?inpAjax=true&responsive=true'
    postData = {'destination':city, 'startDate':startDate, 'endDate':endDate, 'sort':sort, 'page':page}
    data_dic = getData(url, 'post', postData)
    #data_dic = json.loads(data)
    try:
        hotel_pages = data_dic['pagination']['pageCount']
    except KeyError:
        print '%s~%s期间%s没有酒店可供预订酒店'%(startDate, endDate, city)
    else:
        hotel_count = data_dic['pagination']['totalCount']
        print '%s~%s期间%s共有%s家酒店'%(startDate, endDate, city, hotel_count)
        print '共有%s页的数据'%hotel_pages
        hotels_info = []
        hotel_total_num = 1
        hotel_available_num, hotel_unavailable_num = 0 ,0
        for page in range(1, int(hotel_pages)+1):
            print '正在爬取第%s页的数据'%page
            postData = {'destination':city, 'startDate':startDate, 'endDate':endDate, 'sort':sort, 'page':str(page)}
            data_dict = getData(url, 'post', postData)
            if data_dict:
                print '成功获取到第%s页的数据'%page
                #data_dic = json.loads(data)
                hotels = data_dict['results']
                for hotel in hotels:
                    print '找到第%s个酒店的信息'%hotel_total_num
                    hotel_info = {}
                    hotel_basic_info = hotel['retailHotelInfoModel']
                    hotel_id = hotel_basic_info['hotelId']
                    hotel_name_en = hotel_basic_info['hotelName']
                    try:
                        hotel_error_messages = hotel['retailHotelPricingModel']['errorMessages'][0]
                    except KeyError:
                        try:
                            hotel_name_cn = hotel_basic_info['localizedHotelName']
                        except KeyError:
                            hotel_name_cn = ''
                        hotel_address = hotel_basic_info['neighborhood']
                        hotel_address_detailed = hotel_basic_info['hotelDescription']
                        hotel_latitude = hotel_basic_info['latitude']
                        hotel_longitude = hotel_basic_info['longitude']
                        hotel_review = hotel_basic_info['reviewOverall']
                        hotel_tel = hotel_basic_info['telephoneNumber']
                        hotel_url = hotel['infositeUrl']
                        hotel_info['id'] = hotel_id
                        hotel_info['nameEn'] = hotel_name_en
                        hotel_info['nameCn'] = hotel_name_cn
                        hotel_info['address'] = hotel_address
                        hotel_info['addressDetailed'] = hotel_address_detailed
                        hotel_info['latitude'] = hotel_latitude
                        hotel_info['longitude'] = hotel_longitude
                        hotel_info['review'] = hotel_review
                        hotel_info['tel'] = hotel_tel
                        hotel_info['url'] = hotel_url
                        print hotel_id, hotel_name_cn, hotel_name_en, hotel_address, hotel_address_detailed, hotel_latitude, hotel_longitude, hotel_review, hotel_tel, hotel_url
                        print '正在寻找第%s个酒店的房间信息'%hotel_total_num
                        print hotel_url
                        each_hotel_data = getData(hotel_url)
                        if each_hotel_data:
                            soup = BeautifulSoup(each_hotel_data)
                            try:
                                hotel_guest_recommendation = soup.select('span[class="recommend-percentage"]')[0].string.strip()
                            except IndexError:
                                hotel_guest_recommendation = '没有找到客户满意度信息'
                            hotel_info['guest_recommendation'] = hotel_guest_recommendation
                            rooms = soup.select('tbody[class*="room-above-fold"]')
                            print '%s共有%s种房型'%(hotel_name_cn, len(rooms))
                            rooms_info = []
                            for room in rooms:
                                room_info = {'hotel_name':'', 'hotel_id':'', 'hotel_address':'', 'hotel_room_style':'', 'hotel_room_bed_style':'', 'hotel_room_price':'', 'hotel_room_left':'', 'hotel_room_booking_fee':'', 'hotel_room_breakfast':'', 'hotel_room_internet':'', 'hotel_room_refund':'', 'hotel_room_promotional':'', 'hotel_room_booking_status':''}
                                #酒店房型信息
                                try:
                                    hotel_room_style = room.select('div[class="room-basic-info"]')[0].a.text.strip()
                                except IndexError:
                                    hotel_room_style = '房型未知'
                                except AttributeError:
                                    hotel_room_style = room.select('div[class="room-basic-info"]')[0].text.strip()
                                print hotel_room_style
                                #room_info['room_style'] = hotel_room_style
                                #床型信息
                                try:
                                    hotel_room_bed_style_tmp = room.select('div[class="room-basic-info"]')[0].select('div[class*="bed-types"]')[0].text
                                    hotel_room_bed_style = re.sub('\s', '', hotel_room_bed_style_tmp)
                                except IndexError:
                                    hotel_room_bed_style = '床型未知'
                                print hotel_room_bed_style
                                #room_info['bed_style'] = hotel_room_bed_style
                                try:
                                    hotel_room_booking_fee = room.select('td[class="rate-features"]')[0].select('div[class*="no-book-and-fees"]')[0].text.strip()
                                except IndexError:
                                    hotel_room_booking_fee = '预定费未知'
                                print hotel_room_booking_fee
                                #room_info['booking_fee'] = hotel_room_booking_fee
                                try:
                                    hotel_room_refund = room.select('td[class="rate-features"]')[0].select('div[class*="non-refundable"]')[0].text.strip()
                                except IndexError:
                                    hotel_room_refund = '可否退款情况未知'
                                print hotel_room_refund
                                #room_info['refund'] = hotel_room_refund
                                try:
                                    hotel_room_refund_more = room.select('td[class="rate-features"]')[0].select('div[id*="ShowMoreInformationAboutNon-Refundable"]')[0].text.strip()
                                except IndexError:
                                    hotel_room_refund_more = '没有更多退款信息'
                                print hotel_room_refund_more
                                #room_info['refund_more'] = hotel_room_refund_more
                                try:
                                    hotel_room_internet = room.select('td[class="rate-features"]')[0].select('a[href*="internet"]')[0].text.strip()
                                except IndexError:
                                    hotel_room_internet = '能否上网情况未知'
                                print hotel_room_internet
                                #room_info['internet'] = hotel_room_internet
                                try:
                                    hotel_room_breakfast = room.select('td[class="rate-features"]')[0].select('div[id*="breakfast"]')[0].text.strip()
                                except IndexError:
                                    hotel_room_breakfast = '是否提供早餐情况未知'
                                print hotel_room_breakfast
                                #room_info['breakfast'] = hotel_room_breakfast
                                try:
                                    hotel_room_left = room.select('td[class*="avg-rate"]')[0].select('span[class*="room-unavailable-message"]')[0].text.strip()
                                except IndexError:
                                    try:
                                        hotel_room_left = room.select('td[class*="avg-rate"]')[0].select('div[class*="rooms-left"]')[0].text.strip()
                                    except IndexError:
                                        hotel_room_left = '剩余房数未知'
                                    try:
                                        hotel_room_price = room.select('td[class*="avg-rate"]')[0].select('span[class*="room-price"]')[0].text.strip()
                                    except IndexError:
                                        hotel_room_price = '房价未知'
                                    #优惠信息
                                    try:
                                        hotel_room_promotional = room.select('td[class*="avg-rate"]')[0].a.text
                                    except AttributeError:
                                        hotel_room_promotional = '没有促销信息'
                                    print hotel_room_promotional
                                    try:
                                        hotel_room_promotional_more = room.select('td[class*="avg-rate"]')[0].a['data-content']
                                    except :
                                        hotel_room_promotional_more = ''
                                    print hotel_room_promotional_more
                                    try:
                                        hotel_room_booking_status = room.select('td[class*="book-button-column"]')[0].select('span[aria-hidden="true"]')[0].text
                                    except IndexError:
                                        hotel_room_booking_status = '不可预定'
                                else:
                                    hotel_room_booking_status = hotel_room_left
                                    hotel_room_price = ''
                                room_info['hotel_name'] = hotel_name_cn
                                room_info['hotel_id'] = hotel_id
                                room_info['hotel_address'] = hotel_address
                                room_info['hotel_room_style'] = hotel_room_style
                                room_info['hotel_room_bed_style'] = hotel_room_bed_style
                                room_info['hotel_room_price'] = hotel_room_price
                                room_info['hotel_room_left'] = hotel_room_left
                                room_info['hotel_room_promotional'] = hotel_room_promotional + hotel_room_promotional_more
                                room_info['hotel_room_booking_fee'] = hotel_room_booking_fee
                                room_info['hotel_room_refund'] = hotel_room_refund + hotel_room_refund_more
                                room_info['hotel_room_internet'] = hotel_room_internet
                                room_info['hotel_room_breakfast'] = hotel_room_breakfast
                                room_info['hotel_room_booking_status'] = hotel_room_booking_status
                                room_info['city_name'] = city
                                room_info['start_date'] = startDate
                                room_info['end_date'] = endDate
                                print room_info['hotel_name'], room_info['hotel_id'], room_info['hotel_address'], room_info['hotel_room_style'], room_info['hotel_room_bed_style'], room_info['hotel_room_price'], room_info['hotel_room_left'], room_info['hotel_room_promotional'], room_info['hotel_room_booking_fee'], room_info['hotel_room_refund'], room_info['hotel_room_internet'], room_info['hotel_room_breakfast'], room_info['hotel_room_booking_status']
                                rooms_info.append(room_info)
                            writeServer(rooms_info, 'expedia')
                            print '开始插入%s的房间数据'%hotel_name_cn
                            hotel_info['rooms'] = rooms_info
                            hotels_info.append(hotel_info)
                            hotel_total_num += 1
                            hotel_available_num += 1
                        else:
                            print '未找到%s的信息'%hotel_name_cn
                    else:
                        print hotel_name_en + '在' + hotel_error_messages
                        hotel_total_num += 1
                        hotel_unavailable_num += 1
            else:
                print '第%s页出现错误！'%page
        print u'%s~%s期间%s共有%s家酒店,其中可预定的有%s家,已订满的有%s家'%(startDate, endDate, city, hotel_total_num, hotel_available_num, hotel_unavailable_num)
    return


def writeServer(data, table_name):
    conn = MySQLdb.connect (host = "10.0.0.77", user = "root", passwd = "cbj", db = "expedia", port = 3306, charset="utf8")
    cursor = conn.cursor ()
    for i in data:
        city = i['city_name']
        start_date = i['start_date']
        end_date = i['end_date']
        hotel_id = i['hotel_id']
        hotel_name = i['hotel_name']
        hotel_address = i['hotel_address']
        hotel_room_style = i['hotel_room_style']
        hotel_room_bed_style = i['hotel_room_bed_style']
        hotel_room_price = i['hotel_room_price']
        hotel_room_left = i['hotel_room_left']
        hotel_room_promotional = i['hotel_room_promotional']
        hotel_room_booking_fee = i['hotel_room_booking_fee']
        hotel_room_refund = i['hotel_room_refund']
        hotel_room_internet = i['hotel_room_internet']
        hotel_room_breakfast = i['hotel_room_breakfast']
        hotel_room_booking_status = i['hotel_room_booking_status']

        insert_sql = 'INSERT INTO '+table_name+'(CityName,StartDate,EndDate,HotelID,HotelName,HotelAddress,HotelRoomStyle,HotelRoomBedStyle,HotelRoomPrice,HotelRoomLeft,HotelRoomBookingFee,HotelRoomBreakfast,HotelRoomInternet,HotelRoomRefund,HotelRoomPromotional,HotelRoomBookingStatus) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'
        result_insert = cursor.execute(insert_sql, (city,start_date,end_date,hotel_id,hotel_name,hotel_address,hotel_room_style,hotel_room_bed_style,hotel_room_price,hotel_room_left,hotel_room_booking_fee,hotel_room_breakfast,hotel_room_internet,hotel_room_refund,hotel_room_promotional,hotel_room_booking_status))
        conn.commit()
        if result_insert:
            print '插入成功'
        else:
            print '%s酒店的%s插入失败！'%(hotel_name, hotel_room_style)

if __name__ == '__main__':
    url = 'https://www.expedia.cn/Hotel-Search?inpAjax=true&responsive=true'
    #sort = 'recommended'
    sort = 'name'
    """city_list = ['北京','上海', '广州', '深圳', '天津', '重庆', '武汉', '成都', '南京', '杭州']
    #city_list = ['南京', '杭州']
    for city in city_list:
        n = 1
        today = datetime.date.today()
        #today = today + datetime.timedelta(days=10)
        while n < 30:
            tomorrow = today + datetime.timedelta(days=1)
            startDate = today.strftime('%Y/%m/%d')
            endDate = tomorrow.strftime('%Y/%m/%d')
            print '正在查找%s在%s~%s的酒店信息'%(city, startDate, endDate)
            data = getItems(url, city, startDate, endDate, sort)
            today = tomorrow
            n += 1"""

    #测试代码
    city_list = ['北京']
    for city in city_list:
        n = 1
        today = datetime.date.today()
        #today = today + datetime.timedelta(days=10)
        while n < 2:
            tomorrow = today + datetime.timedelta(days=1)
            startDate = today.strftime('%Y/%m/%d')
            endDate = tomorrow.strftime('%Y/%m/%d')
            print '正在查找%s在%s~%s的酒店信息'%(city, startDate, endDate)
            data = getItems(url, city, startDate, endDate, sort)
            today = tomorrow
            n += 1