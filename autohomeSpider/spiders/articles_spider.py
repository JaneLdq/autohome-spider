# -*- coding: utf-8 -*-

from autohomeSpider.items import Article
from requests.exceptions import RequestException
from urllib.parse import urlencode
import scrapy
import requests
import re

class ArticlesSpider(scrapy.Spider):
    name = "articles"

    def start_requests(self, keyword='tesla', *args, **kwargs):
        super(ArticlesSpider, self).__init__(*args, **kwargs)
        params = urlencode({'q': keyword})
        url = 'https://sou.autohome.com.cn/wenzhang?%s' % params
        yield scrapy.Request(url=url, callback=self.parse_search_page)

    def parse_search_page(self, response):
        # crawl all the articles in current page
        for link in response.xpath("//dl[@class='list-dl']/dt/a/@href").extract():
            yield scrapy.Request(url=link, callback=self.parse_article_page)
        # go to next page
        next_page = response.xpath("//a[@class='page-item-next']/@href").extract_first()
        if next_page is not None:
            self.logger.info(next_page)
            yield scrapy.Request(url=next_page, callback=self.parse_search_page)

    def parse_article_page(self, response):
        article = Article()
        # id = re.compile(r'/(\d+).html$', response.url).findall()[0]
        # self.logger.info(str(id))
        # self.logger.info("")
        article['title'] = response.xpath("//div[@id='articlewrap']/h1/text()").extract_first()
        article['date'] = response.xpath("//div[@class='article-info']/span/text()")[0].extract()
        article['content'] = response.xpath("//div[@id='articleContent']/p[not(contains(@class, 'center'))]/text()").extract()

        # get all comments
        comments = []
        # try:
        #     comment_api = "https://reply.autohome.com.cn/api/comments/show.json?id=%s&appid=1&count=0" % id
        #     request = requests.get(comment_api)
        #     self.logger.info(request.json())
        #     comment_list = request.json()['commentlist']
        #     for c in comment_list:
        #         comments.append(c['RContent'])
        # except RequestException:
        #     self.logger.info("Error occurs when get comments from: ", comment_api)
        # finally:
        article['comments'] = comments
        yield article

        # comment_page = response.xpath("//a[@id='hudongreply']/@href").extract()
        # get comments of this article
        # request = scrapy.Request(url=comment_page, callback=parse_comment_page)
        # request.meta['article'] = article
        # yield request


    # def parse_comment_page(self, response):
    #     article = reponse.meta['article']
    #     # add comments in current_page to article
    #     comments = response.xpath("//dl[@id='reply-list']/dd/@datacontent").extract()
    #     article['comments'].append(comments)
    #     # if next page exists, send request
    #     next_page = response.xpath("//a[@class='page-item-next']/@gopages").extract()
    #     if next_page is not None:
    #         request = request
