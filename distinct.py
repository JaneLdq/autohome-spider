from pymongo import MongoClient

client = MongoClient('10.58.0.189', 27017)
db = client.autohome

def distinct_articles():
	db.articles.aggregate(
	    [
	        { "$sort": { "_id": 1 } },
	        { "$group": {
	            "_id": "$id",
	            "doc": { "$first": "$$ROOT" }
	        }},
	        { "$replaceRoot": { "newRoot": "$doc" } },
	        { "$out": "articles" }
	    ]
	)

def distinct_detail():
	db.new_failed_detail_pages.aggregate(
	    [
	        { "$group": {
	            "_id": "$id",
	            "doc": { "$first": "$$ROOT" }
	        }},
	        { "$replaceRoot": { "newRoot": "$doc" } },
	        { "$out": "new_failed_detail_pages" }
	    ]
	)