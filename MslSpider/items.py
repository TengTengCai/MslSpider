# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class MslspiderItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    title = scrapy.Field()
    tag = scrapy.Field()
    categories = scrapy.Field()
    question = scrapy.Field()
    answer = scrapy.Field()
    qa_id = scrapy.Field()
    url_mark = scrapy.Field()
    r_type = scrapy.Field()
    lang = scrapy.Field()
    pass
