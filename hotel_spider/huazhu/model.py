#_*_coding:utf-8 _*_

from sqlalchemy import Column, String, Integer, ForeignKey, create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

def initDB():
    Base.metadata.create_all(engine)

def dropDB():
    Base.metadata.drop_all(engine)


class HotelBasicInfo(Base):
    __tablename__ = 'hotelBasicInfo'
    # 表的结构:
    id = Column(String(20), primary_key=True)
    name = Column(String(256), default=' ', nullable=False)
    nameEn = Column(String(256), default=' ', nullable=False)
    address = Column(String(256), default=' ', nullable=False)
    latitude = Column(String(20), default=' ', nullable=False)
    longitude = Column(String(20), default=' ', nullable=False)
    score = Column(String(20), default=' ', nullable=False)
    commentCount = Column(String(20), default=' ', nullable=False)
    #tel = Column(String(20), default=' ', nullable=False)


class HotelDetailInfo(Base):
    __tablename__ = 'hotelDetailInfo'
    # 表的结构:
    id = Column(Integer, primary_key=True)
    subRoomName = Column(String(256), default=' ', nullable=False)
    checkInDate = Column(String(20), default=' ', nullable=False)
    checkOutDate = Column(String(20), default=' ', nullable=False)
    description = Column(String(256), default=' ', nullable=False)
    bookingState = Column(String(20), default=' ', nullable=False)
    prePay = Column(String(20), default=' ', nullable=False)
    roomLeft = Column(String(20), default=' ', nullable=False)
    returnMoney = Column(String(20), default=' ', nullable=False)
    lowestPrice = Column(String(64), default=' ', nullable=False)
    #price = Column(String(64), default=' ', nullable=False)
    starPrice = Column(String(20), default=' ', nullable=False)
    silverPrice = Column(String(20), default=' ', nullable=False)
    goldenPrice = Column(String(20), default=' ', nullable=False)
    platinumPrice = Column(String(20), default=' ', nullable=False)
    breakfast = Column(String(256), default=' ', nullable=False)
    roomTypeID = Column(String(20), default=' ', nullable=False)
    roomTypeName = Column(String(256), default=' ', nullable=False)
    bedTypeName = Column(String(256), default=' ', nullable=False)
    marketPrice = Column(String(20), default=' ', nullable=False)
    maxCheckInNum = Column(String(256), default=' ', nullable=False)

    hotelId = Column(String(20), ForeignKey('hotelBasicInfo.id', ondelete='CASCADE', onupdate='CASCADE'))

# 初始化数据库连接:
engine = create_engine('mysql+mysqlconnector://root:cbj@localhost:3306/huazhu')
# 创建DBSession类型:
DBSession = sessionmaker(bind=engine)

if __name__ == "__main__":
    initDB()
    #dropDB()
    pass