# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

from scrapy import Item, Field


class SpiderwholesiteItem(Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    id = Field()
    title = Field()
    link = Field()
    author = Field()
    publish_date = Field()
    structure = Field()
    text = Field()
    attachment = Field()

class AttachmentItem(Item):
    link = Field()
    title = Field()
