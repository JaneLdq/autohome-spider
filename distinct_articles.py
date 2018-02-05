from pymongo import MongoClient

client = MongoClient('localhost', 27017)
db = client.autohome
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
