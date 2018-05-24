# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

from scrapy import Item, Field


class CropItem(Item):
    _id = Field()
    crop = Field()
    url = Field()
    title = Field()
    content = Field()
    pub_date = Field()
    source = Field()

class PestItem(Item):
    _id = Field()
    name = Field() # 中文名
    # latin_name = Field() # 拉丁名
    alias = Field() # 别名
    # pathogen_name = Field() # 病原中文名
    # pathogen_latin_name = Field()  # 病原拉丁名
    url = Field()
    type = Field()
    harm_crop = Field() # 主要危害作物
    harm_position = Field() # 主要危害部位
    pest_feature = Field() # 病害特征，病害为该病害对作物造成的特征；虫害为虫的特征；杂草为杂草的特征
    spread_and_occur = Field() # 传播和发生条件
    prevention = Field() # 防治方法
    zone = Field() # 地理分布
    # paper = Field() # 相关文献
    img = Field() # 图片地址
    source = Field() # 数据来源

class PestItem2(Item):
    _id = Field()
    crop = Field()
    url = Field()
    name = Field()
    detail = Field()
    source = Field()
