# 4) Написать запрос к базе, который вернет список подписчиков только указанного пользователя
# 5) Написать запрос к базе, который вернет список профилей, на кого подписан указанный пользователь

from pymongo import MongoClient
from pprint import pprint

client = MongoClient('127.0.0.1',27017)
db = client['instagram']

follow = db.instagram

# DZ 8-4
for line in follow.find({'source_user':'jayanta3383', 'status':'follower'}):
    pprint(line)

# DZ 8-5
for line in follow.find({'source_user':'soumentmc', 'status':'following'}):
    pprint(line)