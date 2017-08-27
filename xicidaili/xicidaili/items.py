# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy import Item, Field


class XicidailiItem(Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    _id = Field()
    ip = Field()
    port = Field()
    address = Field()
    protocol = Field()


