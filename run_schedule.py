from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
import schedule
import time

def run_spider():
    process = CrawlerProcess(get_project_settings())
    process.crawl("feedbacks")
    process.start()

schedule.every(6).hours.do(run_spider)


while True:
    schedule.run_pending()
    time.sleep(1)
