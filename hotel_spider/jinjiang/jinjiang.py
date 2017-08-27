#_*_coding:utf-8 _*_

import requests
import re
import time
import json
import math
import datetime
from bs4 import BeautifulSoup
from db import DBOperator
import sys
reload(sys)
sys.setdefaultencoding('utf-8')


class JinJiang:

    def __init__(self, cityName='', checkInDate='', checkOutDate=''):
        self.cityName = cityName
        self.checkInDate = checkInDate
        self.checkOutDate = checkOutDate
        self.url = 'http://www.jinjianginns.com'

    def getHtml(self, hotelID='', jjCode='', page=1):
        params = {
            "language": "zh-CN",
            "checkInSDate": str(self.checkInDate),
            "checkoutSDate": str(self.checkOutDate),
            "chanel": "WWW",
        }
        header = {
                'Accept': 'application/json, text/javascript, */*; q=0.01',
                'Accept-Encoding': 'gzip, deflate',
                'Accept-Language': 'zh-CN,zh;q=0.8',
                'Connection': 'keep-alive',
                'Content-Type': 'application/json',
                'Host': 'www.jinjianginns.com',
                'Origin': 'http://www.jinjianginns.com',
                'Referer': 'http://www.jinjianginns.com/HotelSearch?cityName=%s&checkinDate=%s&checkoutDate=%s&queryWords=&promoCode=&fulldisname='%(self.cityName,self.checkInDate,self.checkOutDate),
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.110 Safari/537.36',
                'X-Requested-With': 'XMLHttpRequest'
            }
        if hotelID:
            params['HotelIndex'] = '1'
            params['hotelId'] = hotelID
            params['jjCode'] = jjCode
            response = requests.post(self.url+'/service/queryHotelDayPrice', headers=header, data=json.dumps(params))
            data = response.json()
            dataRoom = json.loads(data)
            return dataRoom
        else:
            params['page'] = page
            params['rows'] = '10'
            params['isPromotion'] = 'false'
            params['isScoreExchange'] = 'false'
            params['destination'] = self.cityName
            params['brands'] = 'JJINN,JJDC,JG,BESTAY,BYL'
            print '正在获取第%s页的数据' %page
            response = requests.post(self.url+'/services/queryHotelInfo', headers=header, data=json.dumps(params))
            data = response.json()
            #print data
            dataHotels = json.loads(data)
            return dataHotels

    def getHotels(self, page):
        data = self.getHtml(page=page)
        print '正在解析第%s页的数据' %page
        hotelsInfo = data['HotelInfos']
        cityNameEn = data['enCity']
        hotels = hotelsInfo    #hotels是一个列表
        hotelsBasicInfo = []    #hotelsBasicInfo用来存储所有酒店的基本信息
        IDs = []           #hotelsID用来存储所有酒店的ID
        hotelCurrentNum = 1
        for hotel in hotels:
            print '正在获取第%s页第%s个酒店的数据'%(page, hotelCurrentNum)
            hotelBasicInfo = {}
            hotelBasicInfo['hotelID'] = hotel.get('hotelId')
            hotelBasicInfo['jjCode'] = hotel.get('JjCode')
            hotelBasicInfo['hotelName'] = hotel.get('HotelName')
            hotelBasicInfo['hotelNameEn'] = hotel.get('HotelNameEn', '')
            hotelBasicInfo['hotelAddress'] = hotel.get('Address')
            hotelBasicInfo['hotelLatitude'] = hotel.get('Latitude')
            hotelBasicInfo['hotelLongitude'] = hotel.get('Longitude')
            hotelBasicInfo['hotelScore'] = hotel.get('HotelScore', '')
            hotelBasicInfo['hotelCommentCount'] = hotel.get('ReviewCnt')
            hotelBasicInfo['hotelLowestPrice'] = hotel.get('MinPrice', '')
            hotelBasicInfo['hotelHighestPrice'] = hotel.get('MaxPrice', '')
            print hotelBasicInfo['hotelID'],hotelBasicInfo['jjCode'],hotelBasicInfo['hotelName'],hotelBasicInfo['hotelNameEn'],hotelBasicInfo['hotelAddress'],hotelBasicInfo['hotelLatitude'],hotelBasicInfo['hotelLongitude'],hotelBasicInfo['hotelScore'],hotelBasicInfo['hotelCommentCount'],hotelBasicInfo['hotelLowestPrice'],hotelBasicInfo['hotelHighestPrice']
            hotelsBasicInfo.append(hotelBasicInfo)
            IDs.append([hotelBasicInfo['hotelID'], hotelBasicInfo['jjCode']])
            hotelCurrentNum += 1

        return IDs, hotelsBasicInfo

    def getHotelDetail(self, hotelID, dataRoom):
        print '正在获取ID为%s的酒店的详细信息'%hotelID
        rooms = dataRoom['roomInfos']
        print 'ID为%s的酒店共有%s种房型'%(hotelID, len(rooms))
        if rooms:
            roomsInfo = []
            for room in rooms:
                subRooms = room['plans']
                for subRoom in subRooms:
                    roomInfo = {}
                    roomInfo['hotelID'] = hotelID
                    roomInfo['checkInDate'] = self.checkInDate
                    roomInfo['checkOutDate'] = self.checkOutDate
                    #roomInfo['roomTypeID'] = room.get('RoomType')
                    roomInfo['roomTypeName'] = room.get('RoomType')
                    roomInfo['bedTypeName'] = room.get('BedType')
                    #roomInfo['maxCheckInNum'] = room['Info'].get('MaxCheckInPeopleNum')
                    roomInfo['subRoomName'] = subRoom.get('RateName')
                    #roomInfo['activityID'] = subRoom.get('Activity')
                    #roomInfo['description'] = subRoom.get('Description')
                    roomInfo['marketPrice'] = subRoom.get('marketPrice')
                    roomInfo['price'] = subRoom.get('Price')
                    roomInfo['policy'] = subRoom.get('GuaranteePolicyDes')+';'+subRoom.get('CancelPolicyDes')
                    #roomInfo['internet'] =subRoom.get('IsInternet')
                    #roomInfo['roomLeft'] = subRoom.get('MinStockCount')
                    roomInfo['breakfast'] = subRoom.get('BreakFastCount')
                    #roomInfo['isOverBooked'] = subRoom.get('IsOverBooked')
                    internet = lambda x: '免费' if x else ''
                    roomInfo['internet'] = internet(subRoom.get('IsInternet'))

                    print roomInfo['hotelID'],roomInfo['roomTypeName'],roomInfo['bedTypeName'],roomInfo['subRoomName'],roomInfo['marketPrice'],roomInfo['price'],roomInfo['breakfast'],roomInfo['internet'],roomInfo['policy']
                    roomsInfo.append(roomInfo)
            return roomsInfo
        else:
            print '未找到ID为%s的酒店的房型信息'%hotelID
            return None

    def start(self):
        city_name, city_id, start_date, end_date = '武汉','','2016-08-26','2016-08-27'
        print '正在查找%s在%s~%s的酒店信息'%(city_name, start_date, end_date)
        self.cityName = city_name
        self.checkInDate = start_date
        self.checkOutDate = end_date
        hotelTotalCount = self.getHtml()['PagerRecords']
        totalPages = int(math.ceil(int(hotelTotalCount)/10.0))   #math.ceil(a)取大于或等于的最小整数
        print '%s在%s~%s共有%s家酒店,共有%s页' %(self.cityName, self.checkInDate, self.checkOutDate, hotelTotalCount, totalPages)
        m, n = 0, 0
        errorHotels = {}
        for page in range(1, int(totalPages)+1):
            IDs, hotelsBasicInfo = self.getHotels(page)
            print '正在写入第%s页的数据' %page
            #operator = DBOperator(tableName='HB', data=hotelsBasicInfo)
            #errorHotel = operator.addData()[0]   #把当前页酒店的基本信息写入数据库，一次写入一页数据
            #errorHotels['%s'%page] = errorHotel     #{'第一页'：[错误的ID1,错误的ID2]}
            for ID in IDs:
                hotelID, jjCode = ID
                print hotelID,jjCode
                dataRooms = self.getHtml(hotelID, jjCode)
                roomsInfo = self.getHotelDetail(hotelID, dataRooms)
                if roomsInfo:
                    pass
                    #print '正在写入ID为%s的酒店的所有房型的数据' %hotelID
                    #operator = DBOperator(tableName='HD', data=roomsInfo)
                    #operator.addData()  #把当前酒店的所有房型的全部价格信息写入数据库'''

        print m, n

if __name__ == '__main__':
    jinjiang = JinJiang()
    jinjiang.start()