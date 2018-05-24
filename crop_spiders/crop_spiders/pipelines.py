# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

from pymongo import MongoClient
from crop_spiders.items import CropItem, PestItem, PestItem2



class CropPipeline(object):
    def __init__(self):
        client = MongoClient('localhost', 27017)
        db = client['agri_resource']
        self.crop = db['agri_qa']
        self.pest = db['pest']
        self.pest2 = db['pest2']

    def process_item(self, item, spider):
        if isinstance(item, CropItem):
            self.crop.update({'url': item['url']}, item, True)
        elif isinstance(item, PestItem):
            self.pest.update({'url': item['url']}, item, True)
        elif isinstance(item, PestItem2):
            self.pest2.update({'url': item['url']}, item, True)
        return item