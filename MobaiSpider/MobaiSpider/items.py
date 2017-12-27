# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy import Item, Field


class MobaispiderItem(Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    # _id = Field()
    timestamp = Field()
    currentX = Field()
    currentY = Field()
    bikeIds = Field()
    bikeType = Field()
    distX = Field()
    distY = Field()
    distId = Field()
    distNum = Field()
    distance = Field()
    boundary = Field()
    type = Field()

