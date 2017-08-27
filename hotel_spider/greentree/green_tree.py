#_*_coding:utf-8 _*_

import requests
import re
import time
import math
import datetime
from bs4 import BeautifulSoup
#from db import DBOperator
import sys
reload(sys)
sys.setdefaultencoding('utf-8')


class GreenTree:

    def __init__(self, city_id='', start_date='', end_date=''):
        self.city_id = city_id
        self.start_date = start_date
        self.end_date = end_date
        self.url = 'http://www.998.com/HotelList/SearchHotelList'

    def get_html(self, page=1):
        params = {
            'cityId': self.city_id,
            'hotelCode': '',
            'startDate': self.start_date,
            'endDate': self.end_date,
            # 'promotionType': '',
            # 'HotelTypeId': '',
            # 'areaId': '',
            # 'pointX': '',
            # 'pointY': '',
            # 'PointType': '',
            # 'PointText': '',
            'Sort': 1,
            'SortType': 'asc',
            'PageIndex': page,
            'PageSize': 20
        }
        header = {
            'Accept': '*/*',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'zh-CN,zh;q=0.8',
            'Connection': 'keep-alive',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'Host': 'www.998.com',
            'Origin': 'http://www.998.com',
            'Referer': 'http://www.998.com/HotelList',
            'DNT': 1,
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.110 Safari/537.36',
            'X-Requested-With': 'XMLHttpRequest'
        }

        print '正在获取第%s页的数据' %page
        response = requests.post(self.url, headers=header, data=params)
        if response.status_code != 200:
            return None
        data = response.json()
        return data

    def get_hotels(self, page):
        data = self.get_html(page=page)
        if not data:
            print('未找到第%s页的数据'%(page))
            return
        print '正在解析第%s页的数据' %page
        hotels_info = data
        hotels = hotels_info['HotelInfoViewList']    #hotels是一个列表
        hotels_detail_info = []
        hotelsID = []           #hotelsID用来存储所有酒店的ID
        hotel_current_num = 1
        for hotel in hotels:
            hotels_basic_info = []    #hotelsBasicInfo用来存储所有酒店的基本信息
            print '正在获取第%s页第%s个酒店的数据'%(page, hotel_current_num)
            hotel_basic_info = {}
            hotel_basic_info['hotelID'] = hotel.get('HotelCode', '')
            hotel_basic_info['hotelName'] = hotel.get('HotelName', '')
            hotel_basic_info['hotelNameEn'] = hotel.get('HotelNameEn', '')
            hotel_basic_info['hotelAddress'] = hotel.get('Address', '')
            hotel_basic_info['hotelLatitude'] = hotel.get('Lat', '')
            hotel_basic_info['hotelLongitude'] = hotel.get('Lng', '')
            hotel_basic_info['hotelScore'] = hotel.get('CommentScore', '')
            hotel_basic_info['hotelTotalScore'] = hotel.get('TotalScore', '')
            hotel_basic_info['hotelCommentCount'] = hotel.get('CommentCount', '')
            hotel_basic_info['hotelLowestPrice'] = hotel.get('LowestPrice', '')
            hotel_basic_info['IsFullRoomStatus'] = hotel.get('IsFullRoomStatus', '')
            print hotel_basic_info['hotelID'],hotel_basic_info['hotelName'],hotel_basic_info['hotelNameEn'],hotel_basic_info['hotelAddress'],hotel_basic_info['hotelScore'],hotel_basic_info['hotelCommentCount'],hotel_basic_info['hotelLowestPrice'],hotel_basic_info['IsFullRoomStatus']
            hotels_basic_info.append(hotel_basic_info)
            #print '准备写入%s的信息'%hotelBasicInfo['hotelName']
            #operator = DBOperator(tableName='HB', data=hotelsBasicInfo)
            #operator.addData()   #把当前酒店的基本信息写入数据库，一次写入一条数据
            hotelsID.append(hotel_basic_info['hotelID'])
            hotel_detail_info = self.get_hotel_detail(hotel_basic_info['hotelID'], hotel['RoomTypeList']) #获取当前酒店的详细信息
            hotels_detail_info.append(hotel_detail_info)
            hotel_current_num += 1
        return

    def get_hotel_detail(self, hotelID, detail_info):
        roomsInfo = []
        rooms = detail_info
        print 'ID为%s的酒店共有%s种房型' %(hotelID, len(rooms))
        for room in rooms:
            roomInfo = {}
            roomInfo['hotelID'] = hotelID
            roomInfo['roomTypeID'] = room.get('RoomTypeId', '')     #房间id
            roomInfo['roomTypeName'] = room.get('RoomName', '')
            roomInfo['roomTypeNameEn'] = room.get('RoomNameEn', '')
            roomInfo['roomBedType'] = room.get('D_BedType', '')     #床型
            roomInfo['roomLayer'] = room.get('D_RoomLayer', '')     #入住人数
            roomInfo['checkInDate'] = self.start_date
            roomInfo['checkOutDate'] = self.end_date
            roomInfo['breakfirst'] = room.get('breakfirst', '')     #早餐
            roomInfo['roomStatus'] = room.get('RoomStatus', '')     #是否有房
            roomInfo['totalRooms'] = room.get('TotalRooms', '')
            roomInfo['availRooms'] = room.get('AvailRooms', '')
            #roomInfo['roomLeft'] = room.get('hasRoom', '')
            #roomInfo['lowestPrice'] = room.get('lowestPrice', '')
            #roomInfo['roomRate'] = room.get('roomRate', '')
            roomInfo['marketPrice'] = room.get('MarketPrice', '')           #门市价
            roomInfo['digitalCardRate'] = room.get('DigitalCardRate', '')   #数字卡
            roomInfo['vipCardRate'] = room.get('VipCardRate', '')           #贵宾卡
            roomInfo['goldCardRate'] = room.get('GoldCardRate', '')         #金卡
            roomInfo['platinumCardRate'] = room.get('PlatinumCardRate', '') #铂金卡
            roomInfo['vouchers'] = room.get('Vouchers', '')                 #代金券
            roomInfo['roomReplace'] = room.get('RoomReplace', '')           #兑换
            print roomInfo['hotelID'],roomInfo['roomTypeID'],roomInfo['roomTypeName'],roomInfo['roomTypeNameEn'],roomInfo['roomBedType'],roomInfo['roomLayer'],roomInfo['breakfirst'],roomInfo['roomStatus'],roomInfo['totalRooms'],roomInfo['availRooms'],roomInfo['marketPrice'],roomInfo['digitalCardRate'],roomInfo['vipCardRate'],roomInfo['goldCardRate'],roomInfo['platinumCardRate'],roomInfo['vouchers'],roomInfo['roomReplace']
            roomsInfo.append(roomInfo)
        #print '准备写入ID为%s的酒店的详细数据'%hotelID
        #operator = DBOperator(tableName='HD', data=roomsInfo)
        #operator.addData()  #把当前酒店的所有房型的全部价格信息写入数据库
        return roomsInfo

    def start(self):
        city_name, city_id, start_date, end_date = '北京','226','2016-08-26','2016-08-27'
        print '正在查找%s在%s~%s的酒店信息'%(city_name, start_date, end_date)
        self.city_id = city_id
        self.start_date = start_date
        self.end_date = end_date
        try:
            count = self.get_html()['searchParameters']['TotalCount']
        except Exception as e:
            print('未找到%s在%s~%s的酒店信息,error:%s'%(city_name, start_date, end_date, e))
        else:
            pages = int(math.ceil(count/20.0))   #math.ceil(a)取大于或等于的最小整数
            print '%s在%s~%s共有%s家酒店,共有%s页' %(city_name, start_date, end_date, count, pages)
            start = time.time()
            for page in range(1, int(pages)+1):
                self.get_hotels(page)
            print '持续时间：',time.time()-start

if __name__ == '__main__':
    gt = GreenTree()
    gt.start()