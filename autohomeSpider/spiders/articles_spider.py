# -*- coding: utf-8 -*-

from autohomeSpider.items import Article
from requests.exceptions import RequestException
from urllib.request import urlopen
from urllib.parse import quote
import json
import scrapy
import re

class ArticlesSpider(scrapy.Spider):
    name = "articles"

    def start_requests(self, keyword='特斯拉', *args, **kwargs):
        super(ArticlesSpider, self).__init__(*args, **kwargs)
        keyword = quote(keyword.encode('gb2312'))
        url = 'https://sou.autohome.com.cn/wenzhang?q=%s' % keyword
        yield scrapy.Request(url=url, callback=self.parse_search_page)

    def parse_search_page(self, response):
        # crawl all the articles in current page
        for link in response.xpath("//dl[@class='list-dl']/dt/a/@href").extract():
            yield scrapy.Request(url=link, callback=self.parse_article_page)
        # go to next page
        next_page = response.xpath("//a[@class='page-item-next']/@href").extract_first()
        if next_page is not None:
            yield response.follow(url=next_page, callback=self.parse_search_page)

    def parse_article_page(self, response):
        article = Article()
        article['id'] = re.compile(r'.*/(\d+).html$').findall(response.url)[0]
        article['title'] = response.xpath("//div[@id='articlewrap']/h1/text()").extract_first().strip()
        article['date'] = response.xpath("//div[@class='article-info']/span/text()")[0].extract().strip()
        # TODO extract all plain text
        article['content'] = response.xpath("//div[@id='articleContent']/p[not(contains(@class, 'center'))]/text()").extract()
        # get all comments
        comments = []
        try:
            comment_api = 'https://reply.autohome.com.cn/api/comments/show.json?id=%s&appid=1&count=0' % article['id']
            request = json.load(urlopen(comment_api))
            for c in request['commentlist']:
                comments.append(c['RContent'])
        except (URLError, HTTPError, JSONDecodeError):
            self.logger.info("Error occurs when get comments from: ", comment_api)
        finally:
            article['comments'] = comments
            yield article
