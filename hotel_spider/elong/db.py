#_*_coding:utf-8 _*_
from pymongo import MongoClient

client = MongoClient('localhost', 27017)
elong = client['elong']
hotel_id = elong['hotel_id']      #所有酒店的id
hotel_basic_info = elong['hotel_basic_info']
hotel_detail_info = elong['hotel_detail_info']  #每个酒店的详细信息