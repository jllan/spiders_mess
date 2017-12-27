# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

import csv
from datetime import datetime
from os import path
from pymongo import MongoClient

class MobaispiderPipeline(object):
    def __init__(self):
        client = MongoClient('127.0.0.1', 27017)
        db = client['BikeSharing']
        self.collection = db['mobai']
        self.current_time = datetime.now().strftime('%Y%m%d-%H%M%S')

    def process_item(self, item, spider):
        item = dict(item)
        self.collection.insert(item)
        with open(path.join('csvfile', self.current_time+".csv"), "a+") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(item.values())
        return item
