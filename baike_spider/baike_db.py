#coding:utf-8
from pymongo import MongoClient

client = MongoClient('localhost', 17027)
baike_db = client['baike']
baike = baike_db['baike']