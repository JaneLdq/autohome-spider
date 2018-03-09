# -*- coding: utf-8 -*-
import scrapy


class Article(scrapy.Item):
    # define the fields for your item here like:
    id = scrapy.Field()
    title = scrapy.Field()
    date = scrapy.Field()
    content = scrapy.Field()
    comments = scrapy.Field()
    tags = scrapy.Field()

class Feedback(scrapy.Item):
    # car series id
    page_id = scrapy.Field()
    series_id = scrapy.Field()
    # car series name
    series_name = scrapy.Field()
    # a list of purposes of use
    purposes = scrapy.Field()
    title = scrapy.Field()
    # [{date, content}]
    items = scrapy.Field()
