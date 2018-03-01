# -*- coding: utf-8 -*-

from autohomeSpider.items import Feedback
from requests.exceptions import RequestException
from urllib.request import urlopen
from urllib.parse import quote
import json
import scrapy
import re

class FeedbacksSpider(scrapy.Spider):
    name = "feedbacks"

    custom_settings = {
        'ITEM_PIPELINES': {
            'autohomeSpider.pipelines.FeedbackMongoPipeline': 300
        }
    }

    def start_requests(self, level=None):
        url = 'https://k.autohome.com.cn/ajax/getSceneSelectCar?minprice=2&maxprice=110&_appid=koubei'
        if level:
            url += '&level=' + level
        car_list = json.load(urlopen(url))
        for car in car_list['result']:
            link = 'https://k.autohome.com.cn/' + str(car['SeriesId'])
            self.logger.info("Crawling feedback of car series: %s" % link)
            yield scrapy.Request(url=link, callback=self.parse_feedback_list)

    def parse_feedback_list(self, response):
        # crawl all the articles in current page
        links = response.xpath("//div[@class='mouthcon']//div[contains(@class, 'title-name')]/a/@href").extract()
        for link in links:
            self.logger.info("Crawling feedback detail page: %s" % link)
            yield response.follow(url=link, callback=self.parse_feedback_page)
        # go to next page
        next_page = response.xpath("//a[@class='page-item-next']/@href").extract_first()
        self.logger.info("Next page: %s" % next_page)
        if next_page is not None:
            yield response.follow(url=next_page, callback=self.parse_feedback_list)

    def parse_feedback_page(self, response):
        feedback = Feedback()
        feedback['series_name'] = response.xpath("//div[@class='subnav-title-name']/a/text()").extract_first().strip()
        feedback['purposes'] = response.xpath("//div[@class='mouthcon-cont-left']/div[@class='choose-con']/p[@class='obje']/text()").extract().strip()
        feedback['title'] = response.xpath("//div[@class='mouthcon-cont-right']/div[@class='mouth-main']/div[@class='kou-tit']/h3/text()").extract_first().strip()

        # extract text from each <div class='mouth-item'> block
        origin_content_list = response.xpath("//div[@class='mouthcon-cont-right']/div[@class='mouth-main']/div[@class='mouth-item']/div[@class='text-con']").extract()
        content_list = []
        regexp = re.compile(r'(<[^>]*>)|(\xa0)')
        for item in origin_content_list:
            content_list.append(regexp.sub('', item).strip())
        feedback['content_list'] = content_list

        yield feedback
