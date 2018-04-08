from urllib2  import urlopen
from pymongo import MongoClient
import ssl
import json

client = MongoClient('localhost', 27017)
db = client.autohome

url = 'https://k.autohome.com.cn/ajax/getSceneSelectCar?minprice=2&maxprice=110&_appid=koubei'
car_list = json.load(urlopen(url, context=ssl._create_unverified_context()))['result']

series_ids = map(lambda c: {'id': c['SeriesId']}, car_list)

db.new_series_id.insert_many(series_ids)
