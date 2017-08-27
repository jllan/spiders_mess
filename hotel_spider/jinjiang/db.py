#_*_coding:utf-8 _*_

from model import HotelBasicInfo, HotelDetailInfo, DBSession

HB = HotelBasicInfo
HD = HotelDetailInfo
session = DBSession()


class DBOperator():
    def __init__(self, tableName, data):
        self.dbName = tableName
        self.data = data
        self.errorRooms = []     #用来记录写入错误的数据
        self.errorHotels = []

    def addData(self):
        if self.dbName == 'HB':
            for data in self.data:
                newData = HB(id = data['hotelID'],
                       name = data['hotelName'],
                       nameEn = data.get('hotelNameEn'),
                       address = data['hotelAddress'],
                       latitude = data['hotelLatitude'],
                       longitude = data['hotelLongitude'],
                       score = data['hotelScore'],
                       #tel=data['hotelTel'])
                       commentCount = data['hotelCommentCount'])
                session.add(newData)
                try:
                    session.commit()
                except Exception, e:
                    print e
                    self.errorHotels.append(data['hotelID'])
                    if 'Duplicate entry' in e:
                        print '数据重复输入'
            session.close()

        if self.dbName == 'HD':
            for data in self.data:
                newData = HD(
                       roomTypeID = data.get('roomTypeID'),
                       roomTypeName = data.get('roomTypeName'),
                       bedTypeName = data.get('bedTypeName'),
                       subRoomName = data.get('subRoomName'),
                       checkInDate = data['checkInDate'],
                       checkOutDate = data['checkOutDate'],
                       roomLeft = data.get('roomLeft'),
                       bookingState = data.get('bookingState'),
                       description = data.get('description'),
                       lowestPrice=data.get('lowestPrice'),
                       price = data.get('price'),
                       marketPrice = data.get('marketPrice'),
                       starPrice = data.get('starPrice'),
                       silverPrice = data.get('silverPrice'),
                       goldenPrice = data.get('goldenPrice'),
                       platinumPrice = data.get('platinumPrice'),
                       prePay = data.get('prePay'),
                       breakfast = data.get('breakfast'),
                       returnMoney = data.get('returnMoney'),
                       maxCheckInNum = data.get('maxCheckInNum'),
                       hotelId = data['hotelID'])
                session.add(newData)
                try:
                    session.commit()
                except Exception, e:
                    print 'error:', e
                    self.errorRooms.append(data['hotelID'])
            session.close()
        return self.errorHotels, self.errorRooms


    def delData(self):
        pass

    def queryData(self):
        pass


