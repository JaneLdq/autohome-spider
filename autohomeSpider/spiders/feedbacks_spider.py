# -*- coding: utf-8 -*-

from autohomeSpider.items import Feedback
from requests.exceptions import RequestException
from urllib.request import urlopen
from urllib.parse import quote
from http.cookies import SimpleCookie
from bs4 import BeautifulSoup
import json
import scrapy
import re
import ssl

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
        'user-agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.186 Safari/537.36",
        'accept': "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
        'accept-encoding': "gzip, deflate, br",
        'accept-language': "en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7,zh-TW;q=0.6",
        'cache-control': "no-cache",
    }

    meta_no_redirect = {
         'dont_redirect': True,
         'handle_httpstatus_list': [302]
    }

    def start_requests(self, level=None):
        # url = 'https://k.autohome.com.cn/ajax/getSceneSelectCar?minprice=2&maxprice=110&_appid=koubei'
        # if level:
        #     url += '&level=' + level
        #
        # car_list = json.load(urlopen(url, context=ssl._create_unverified_context()))
        # for car in car_list['result']:
        #     link = 'https://k.autohome.com.cn/' + str(car['SeriesId'])
        #     self.logger.info("Crawling feedback of car series: %s" % link)
        #     yield scrapy.Request(url=link, headers=self.headers, callback=self.parse_feedback_list)

        # test
        # link = 'https://k.autohome.com.cn/4246'
        # self.logger.info("Crawling feedback of car series: %s" % link)
        # yield scrapy.Request(url=link, headers=self.headers, meta=self.meta_no_redirect, callback=self.parse_feedback_list)

        link = 'https://k.autohome.com.cn/detail/view_01br7syny564v3jc9n74w00000.html?st=7&piap=0|4073|0|0|1|0|0|0|0|0|1'
        self.logger.info("Crawling feedback of detail: %s" % link)
        yield scrapy.Request(url=link, headers=self.headers, meta=self.meta_no_redirect, callback=self.parse_feedback_page)

    def parse_feedback_list(self, response):
        # redirect with token
        if response.status == 302:
            redirect_url = str(response.headers.get('Location'), 'utf-8')
            yield scrapy.Request(url=redirect_url, dont_filter=True, callback=self.parse_feedback_list)

        # get the feedback list for the specific car series
        links = response.xpath("//div[@class='mouthcon']//div[contains(@class, 'title-name')]/a/@href").extract()
        for link in links:
            self.logger.info("Crawling feedback detail page: %s" % link)
            yield response.follow(url=link, headers=self.headers, callback=self.parse_feedback_page)

        # go to next page
        next_page = response.xpath("//a[@class='page-item-next']/@href").extract_first()
        if next_page is not None:
            yield response.follow(url=next_page, callback=self.parse_feedback_list)

    def parse_feedback_page(self, response):
        if response.status == 302:
            redirect_url = str(response.headers.get('Location'), 'utf-8')
            yield scrapy.Request(url=redirect_url, dont_filter=True, callback=self.parse_feedback_page)

        feedback = Feedback()
        feedback['series_name'] = response.xpath("//div[@class='subnav-title-name']/a/text()").extract_first().strip()
        feedback['purposes'] = response.xpath("//div[@class='mouthcon-cont-left']/div[@class='choose-con']//p[@class='obje']/text()").extract()
        feedback['title'] = response.xpath("//div[@class='mouth-main']//div[@class='kou-tit']/h3/text()").extract_first().strip()

        # extract text from each <div class='mouth-item'> block
        origin_content_list = response.xpath("//div[@class='mouthcon-cont-right']/div[@class='mouth-main']/div[@class='mouth-item']/div[@class='text-con']").extract()
        content_list = []
        for item in origin_content_list:
            soup = BeautifulSoup(item)
            for s in soup(['script', 'style']):
                s.decompose()
            content = ''.join(soup.stripped_strings)
            content_list.append(content)
            break;
        feedback['content_list'] = content_list

        yield feedback

    def clean_content(html):
        soup = BeautifulSoup(html)
        for s in soup(['script', 'style']):
            s.decompose()
        return ''.join(soup.stripped_strings)
