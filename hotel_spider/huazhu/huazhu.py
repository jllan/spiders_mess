#_*_coding:utf-8 _*_

import requests
import re
import time
import math
import datetime
from bs4 import BeautifulSoup
from db import DBOperator
import sys
reload(sys)
sys.setdefaultencoding('utf-8')


class HuaZhu:

    def __init__(self, cityID='', checkInDate='', checkOutDate=''):
        self.cityID = cityID
        self.checkInDate = checkInDate
        self.checkOutDate = checkOutDate
        self.url = 'http://hotels.huazhu.com'
        self.urlM = 'http://m.huazhu.com'       #手机端地址

    def getHtml(self, page=1):
        params = {
            #'CityID': self.cityID,
            #'HotelID':HotelID,
            'CheckInDate': self.checkInDate,
            'CheckOutDate': self.checkOutDate
        }
        header = {
                'Accept': '*/*',
                'Accept-Encoding': 'gzip, deflate, sdch',
                'Accept-Language': 'zh-CN,zh;q=0.8',
                'Connection': 'keep-alive',
                'Host': 'hotels.huazhu.com',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.110 Safari/537.36',
            }

        print '正在获取第%s页的数据' %page
        params['CityID'] = self.cityID
        vt = re.findall("__v_t = '(.*?)';", requests.get(self.url, headers=header, params=params).content)[0] #获取__v_t
        header['__v_t'] = vt
        header['X-Requested-With'] = 'XMLHttpRequest'
        params['_'] = int(time.time()*1000)
        params['PageIndex'] = page
        response = requests.get(self.url+'/Search/HotelList', headers=header, params=params)
        data = response.json()
        return data

    '''请求电脑端页面获取所有酒店的基本信息，包括酒店的ID'''
    def getHotels(self, page):
        data = self.getHtml(page=page)
        hotelsInfo = data
        print '正在解析第%s页的数据' %page
        hotelTotalCount = hotelsInfo['TotalCount']
        cityName = hotelsInfo['CityName']
        #totalPages = int(math.ceil(hotelTotalCount/10.0))   #math.ceil(a)取大于或等于的最小整数
        #print '%s在%s~%s共有%s家酒店,共有%s页' %(cityName, self.checkInDate, self.checkOutDate, hotelTotalCount, totalPages)
        hotels = hotelsInfo['HotelList']    #hotels是一个列表
        hotelsBasicInfo = []    #hotelsBasicInfo用来存储所有酒店的基本信息
        hotelsID = []           #hotelsID用来存储所有酒店的ID
        hotelCurrentNum = 1
        for hotel in hotels:
            print '正在获取第%s页第%s个酒店的数据'%(page, hotelCurrentNum)
            hotelBasicInfo = {}
            hotelBasicInfo['hotelID'] = hotel.get('HotelID', '')
            hotelBasicInfo['hotelName'] = hotel.get('HotelName', '')
            hotelBasicInfo['hotelNameEn'] = hotel.get('HotelNameEn', '')
            hotelBasicInfo['hotelAddress'] = hotel.get('HotelAddressShort', '')
            hotelBasicInfo['hotelLatitude'] = hotel.get('Lat', '')
            hotelBasicInfo['hotelLongitude'] = hotel.get('Lng', '')
            hotelBasicInfo['hotelScore'] = hotel.get('HotelScore', '')
            hotelBasicInfo['hotelCommentCount'] = hotel.get('HotelCommentCount', '')
            #hotelBasicInfo['hotelLowestPrice'] = hotel.get('HotelLowestPrice', '')
            print hotelBasicInfo['hotelID'],hotelBasicInfo['hotelName'],hotelBasicInfo['hotelNameEn'],hotelBasicInfo['hotelAddress'],hotelBasicInfo['hotelLatitude'],hotelBasicInfo['hotelLongitude'],hotelBasicInfo['hotelScore'],hotelBasicInfo['hotelCommentCount']
            hotelsBasicInfo.append(hotelBasicInfo)
            hotelsID.append(hotelBasicInfo['hotelID'])

            #getHotelDetail(hotelBasicInfo['hotelID'], checkInDate, checkOutDate) #获取当前酒店的详细信息
            hotelCurrentNum += 1

        return hotelsID, hotelsBasicInfo

    '''根据酒店ID从手机端获取每个酒店的详细信息，然后再根据酒店ID和该酒店的房型信息从手机端获取每个房型的价格'''
    def getHotelDetailM(self, hotelID):
        print '正在获取ID为%s的酒店的详细信息'%hotelID
        session = requests.session()
        param = {
            'HotelID': hotelID,
            'CheckInDate': self.checkInDate,
            'CheckOutDate': self.checkOutDate
        }
        url = 'http://m.huazhu.com/hotel/detail'
        header = {
                'Accept': '*/*',
                'Accept-Encoding': 'gzip, deflate, sdch',
                'Accept-Language': 'zh-CN,zh;q=0.8',
                'Connection': 'keep-alive',
                'Host': 'm.huazhu.com',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.110 Safari/537.36',
            }
        response = session.get(url, params=param, headers=header)
        patternRooms = re.compile('ndoo.vars.rooms = (\[.*?\]);')
        rooms = re.findall(patternRooms, response.content)[0]
        false, true, null = 'false', 'true', 'null' #rooms的关键字
        rooms = eval(rooms)
        if rooms:
            roomsInfo = []
            for room in rooms:
                subRooms = room['Details']
                for subRoom in subRooms:
                    roomInfo = {}
                    roomInfo['hotelID'] = hotelID
                    roomInfo['checkInDate'] = self.checkInDate
                    roomInfo['checkOutDate'] = self.checkOutDate
                    roomInfo['roomTypeID'] = room.get('RoomTypeID')
                    roomInfo['roomTypeName'] = room.get('RoomTypeName')
                    roomInfo['marketPrice'] = room.get('MarketPrice')
                    roomInfo['bedTypeName'] = room['Info'].get('BedType')
                    #roomInfo['roomNum'] = room['Info'].get('RoomNum')
                    roomInfo['maxCheckInNum'] = room['Info'].get('MaxCheckInPeopleNum')
                    roomInfo['subRoomName'] = subRoom.get('Name')
                    #roomInfo['activityID'] = subRoom.get('Activity')
                    description = lambda x: '' if x=='null' else x
                    roomInfo['description'] = description(subRoom.get('Description'))
                    #roomInfo['description'] = subRoom.get('Description')
                    roomInfo['lowestPrice'] = subRoom.get('Price')
                    roomInfo['roomLeft'] = subRoom.get('MinStockCount')
                    roomInfo['returnMoney'] = subRoom.get('OrderFirstReturnMoney')
                    roomInfo['breakfast'] = subRoom.get('BreakfastCount')
                    #roomInfo['isOverBooked'] = subRoom.get('IsOverBooked')
                    booked = lambda x: '预定' if x=='false' else '满房'
                    roomInfo['bookingState'] = booked(subRoom.get('IsOverBooked'))
                    pay = lambda x: '预付' if x=='true' else ''
                    roomInfo['prePay'] = pay(subRoom.get('IsMustOnlinePay'))
                    roomInfo['platinumPrice'],roomInfo['goldenPrice'],roomInfo['silverPrice'],roomInfo['starPrice'] = '','','',''
                    print roomInfo['hotelID'],roomInfo['roomTypeID'],roomInfo['roomTypeName'],roomInfo['subRoomName'],roomInfo['returnMoney'],roomInfo['breakfast'],roomInfo['bookingState'],roomInfo['roomLeft']
                    if subRooms.index(subRoom) == 0 and subRoom['MemberLevel']!= 'null':     #只有第一项才有会员价格的数据
                        memberPrice = self.getRoomPriceM(hotelID, roomInfo['roomTypeID'], session)
                        if memberPrice:
                            roomInfo['platinumPrice'],roomInfo['goldenPrice'],roomInfo['silverPrice'],roomInfo['starPrice'] = memberPrice
                    print roomInfo['platinumPrice'],roomInfo['goldenPrice'],roomInfo['silverPrice'],roomInfo['starPrice']
                    roomsInfo.append(roomInfo)
            return roomsInfo
        else:
            print '未找到ID为%s的酒店的房型信息'%hotelID
            return None

    '''国际酒店'''
    def getHotelDetailIntM(self, hotelID):
        print '正在获取ID为%s的酒店的详细信息，该酒店是国际酒店'%hotelID
        session = requests.session()
        url = 'http://m.huazhu.com/Hotel/Interdetail?hotelId=%s&checkInDate=%s&checkOutDate=%s'%(hotelID, self.checkInDate, self.checkOutDate)
        session.get(url)        #先请求一次获取session
        param = {
            'isEn': 'False',
            'roomCount': '1',
            'guestPerRoom': '1'
        }
        url = 'http://m.huazhu.com/Hotel/InterDetailRoom'
        header = {
                'Accept': '*/*',
                'Accept-Encoding': 'gzip, deflate, sdch',
                'Accept-Language': 'zh-CN,zh;q=0.8',
                'Connection': 'keep-alive',
                'Host': 'm.huazhu.com',
                'Referer': 'http://m.huazhu.com/Hotel/Interdetail?hotelId=%s&checkInDate=%s&checkOutDate=%s'%(hotelID, self.checkInDate, self.checkOutDate),
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.110 Safari/537.36',
                'X-Requested-With': 'XMLHttpRequest'
            }
        response = session.get(url, params=param, headers=header)
        soup = BeautifulSoup(response.text, 'lxml')
        rooms = soup.findAll('div',{'class':'roomitem'})
        print 'hotelID为%s的酒店有%s种房型'%(hotelID, len(rooms))
        roomsInfo = []
        for room in rooms:
            subRooms = room.select('div[class*="subitem"]')
            for subRoom in subRooms:
                roomInfo = {}
                roomInfo['hotelID'] = hotelID
                roomInfo['checkInDate'] = self.checkInDate
                roomInfo['checkOutDate'] = self.checkOutDate
                roomInfo['roomTypeID'] = room['data-roomcode']
                roomInfo['roomTypeName'] = room.find('',{'class':'roomtype'}).text

                roomInfo['subRoomName'] = subRoom.h3.text.strip()
                roomInfo['description'] = subRoom.div.div.text.strip().replace('\n', ' ')
                roomInfo['marketPrice'] = subRoom.select('div[class*="price"]')[0].text.replace('\n', '')
                roomInfo['bookingState'] = subRoom.select('div[class*="rbtnarea"]')[0].text.strip()
                print roomInfo['roomTypeID'],roomInfo['roomTypeName'],roomInfo['subRoomName'],roomInfo['description'],roomInfo['marketPrice'],roomInfo['bookingState']
                roomsInfo.append(roomInfo)
        return roomsInfo

    def getRoomPriceM(self, hotelID, roomID, session, tryNum=1):
        print '正在获取ID为%s的酒店%s房型的价格信息'%(hotelID, roomID)
        url = 'http://m.huazhu.com/Hotel/Price'
        data = {
            'roomTypeID': roomID,
            'activityID':''
        }
        header = {
                'Accept': '*/*',
                'Accept-Encoding': 'gzip, deflate',
                'Accept-Language': 'zh-CN,zh;q=0.8',
                'Connection': 'keep-alive',
                'Content-Type': 'application/x-www-form-urlencoded',
                'Host': 'm.huazhu.com',
                'Origin': 'http://m.huazhu.com',
                'Referer': 'http://m.huazhu.com/Hotel/Detail?hotelId=%s&checkInDate=%s&checkOutDate=%s'%(hotelID, self.checkInDate, self.checkOutDate),
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.110 Safari/537.36',
                'X-Requested-With': 'XMLHttpRequest'
            }
        response = session.post(url, headers=header, data=data)
        try:
            prices = response.json()['Data']['PriceCalender']
        except Exception, e:
            print 'error:',e
            if tryNum < 2:
                print 'try again!'
                tryNum += 1
                self.getRoomPriceM( hotelID, roomID, session, tryNum)
            else:
                return None
        else:
            roomPrices = []
            for price in prices:
                roomPrice = price['DailyRoomPriceOfMemberList'][0]['Price']
                roomPrices.append(roomPrice)
            return roomPrices

    def start(self):
        city_name, city_id, start_date, end_date = '上海','3101','2016-08-26','2016-08-27'
        print '正在查找%s在%s~%s的酒店信息'%(city_name, start_date, end_date)
        self.cityID = city_id
        self.checkInDate = start_date
        self.checkOutDate = end_date
        hotelTotalCount = self.getHtml()['TotalCount']
        totalPages = int(math.ceil(hotelTotalCount/10.0))   #math.ceil(a)取大于或等于的最小整数
        print '%s在%s~%s共有%s家酒店,共有%s页' %(city_name, self.checkInDate, self.checkOutDate, hotelTotalCount, totalPages)
        m, n = 0, 0     #用来记录国内和国际酒店的数量
        #errorHotels = {}
        for page in range(1, int(totalPages)+1):
            #data = self.getHtml(page=page)
            hotelsID, hotelsBasicInfo = self.getHotels(page)
            print '正在写入第%s页的数据' %page
            #operator = DBOperator(tableName='HB', data=hotelsBasicInfo)
            #errorHotel = operator.addData()[0]   #把当前页酒店的基本信息写入数据库，一次写入一页数据
            #errorHotels['%s'%page] = errorHotel     #{'第一页'：[错误的ID1,错误的ID2]}
            for hotelID in hotelsID:
                if len(hotelID) > 4:
                    roomsInfo = self.getHotelDetailM(hotelID)
                    m += 1
                else:
                    print hotelID
                    roomsInfo = self.getHotelDetailIntM(hotelID)
                    n += 1
                if roomsInfo:
                    pass
                    #print '正在写入ID为%s的酒店的所有房型的数据' %hotelID
                    #operator = DBOperator(tableName='HD', data=roomsInfo)
                    #operator.addData()  #把当前酒店的所有房型的全部价格信息写入数据库
        print m, n
        #print errorHotels

if __name__ == '__main__':
    huazhu = HuaZhu()
    huazhu.start()