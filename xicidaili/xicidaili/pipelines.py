# -*- coding: utf-8 -*-
import pymongo
# from .items import XicidailiItem

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html


class XicidailiPipeline(object):
    def __init__(self):
        client = pymongo.MongoClient('localhost', 27017)
        db = client['Proxies']
        self.proxies = db['proxies']

    def process_item(self, item, spider):
        self.proxies.insert_one(item)
        return item
