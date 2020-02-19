# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class NemsspiderItem(scrapy.Item):
    # define the fields for your item here like:
    msg = scrapy.Field()
    headers = scrapy.Field()
    lists = scrapy.Field()
    is_update = scrapy.Field()
    first_week_day = scrapy.Field()


class DecspiderItem(scrapy.Item):
    # define the fields for your item here like:
    msg = scrapy.Field()
    is_update = scrapy.Field()
    first_week_day = scrapy.Field()
    all_info = scrapy.Field()


class DWDecspiderItem(scrapy.Item):
    # define the fields for your item here like:
    msg = scrapy.Field()
    is_update = scrapy.Field()
    first_week_day = scrapy.Field()
    all_info = scrapy.Field()
