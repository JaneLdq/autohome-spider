# -*- coding: utf-8 -*-

from scrapy.spidermiddlewares.httperror import HttpError
from autohomeSpider.items import Feedback
from urllib2 import urlopen
from bs4 import BeautifulSoup
from autohomeSpider.font import Font
from autohomeSpider.script_decoder import *
from pymongo import MongoClient
import json
import scrapy
import re
import ssl

client = MongoClient('10.58.0.189', 27017)
db = client.autohome


detail_page_regex = re.compile("//k.autohome.com.cn/detail/view_([\d\w]+).html")


class FeedbacksSpider(scrapy.Spider):
    name = "feedbacks"

    custom_settings = {
        'ITEM_PIPELINES': {
            'autohomeSpider.pipelines.FeedbackMongoPipeline': 300
        }
    }

    headers = {
        'host': "k.autohome.com.cn",
        'connection': "keep-alive",
        'upgrade-insecure-requests': "1",
        'accept': "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
        'accept-encoding': "gzip, deflate, br",
        'accept-language': "en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7,zh-TW;q=0.6",
        'cache-control': "no-cache",
    }

    meta_no_redirect = {
         'dont_redirect': True,
         'handle_httpstatus_list': [302, 404]
    }

    def start_requests(self, level=None):
        series_ids = db.series_id.find({})
        for doc in series_ids:
            link = link = 'https://k.autohome.com.cn/' + str(doc['id'])
            yield scrapy.Request(url=link, headers=self.headers, dont_filter=True, callback=self.parse_feedback_list, meta={'series_id': doc['id']})

        failed_detail_ids = db.failed_fb_detail_pages.find({})
        for doc in failed_detail_ids:
            link = 'https://k.autohome.com.cn/detail/view_' + str(doc['id']) + '.html'
            yield scrapy.Request(url=link, headers=self.headers, dont_filter=True, callback=self.parse_feedback_page, errback=self.errback_httpbin, meta={'series_id': doc['series_id']})



    def parse_feedback_list(self, response):
        self.logger.info("Crawling feedback of car series: %s" % response.meta['series_id'])

        # get the feedback list for the specific car series
        links = response.xpath("//div[@class='mouthcon']//div[contains(@class, 'title-name')]/a/@href").extract()
        for link in links:
            yield response.follow(url=link, headers=self.headers, dont_filter=True, callback=self.parse_feedback_page, errback=self.errback_httpbin, meta=response.meta)

        # go to next page
        next_page = response.xpath("//a[@class='page-item-next']/@href").extract_first()
        if next_page is not None:
            yield response.follow(url=next_page, callback=self.parse_feedback_list, dont_filter=True, meta=response.meta)
        else:
            # if successfully crawled the whole list page of one series, then delete the series id from db
            db.series_id.find_one_and_delete({'id': response.meta['series_id']})


    def parse_feedback_page(self, response):
        self.logger.info("Crawling feedback detail page: %s" % response.meta)
        
        page_id = re.search(detail_page_regex, response.url).group(1)
        db.failed_fb_detail_pages.find_one_and_delete({'id': page_id})

        feedback = Feedback()
        feedback['page_id'] = page_id
        feedback['series_name'] = response.xpath("//div[@class='subnav-title-name']/a/text()").extract_first().strip()
        feedback['series_id'] = response.meta['series_id']
        feedback['purposes'] = response.xpath("//div[@class='mouthcon-cont-left']/div[@class='choose-con']//p[@class='obje']/text()").extract()
        feedback['title'] = response.xpath("//div[@class='mouth-main']//div[@class='kou-tit']/h3/text()").extract_first().strip()

        # get dynamic self-defined font
        regex = re.compile("url\('(//.*.ttf)'\) format\('woff'\)")
        font_url = re.findall(regex, response.body)[0]
        font = Font(font_url)

        # extract text from each <div class='mouth-item'> block
        origin_content_list = response.xpath("//div[@class='mouthcon-cont-right']/div[@class='mouth-main']/div[@class='mouth-item']/div[@class='text-con']").extract()
        content_list = []
        for item in origin_content_list:
            content_list.append(decode(item, font))
        feedback['items'] = content_list
        yield feedback

    def errback_httpbin(self, failure):
        if failure.check(HttpError):
            response = failure.value.response
            if response.status == 404:
                if re.search(detail_page_regex, response.url):
                    failed_detail_id = re.search(detail_page_regex, response.url).group(1)
                    # keep this detail page in db for later try
                    db.failed_fb_detail_pages.insert_one({'id': failed_detail_id, 'series_id': response.meta['series_id']})

                    self.logger.info('Failed detail page request: %s' % failed_detail_id)
