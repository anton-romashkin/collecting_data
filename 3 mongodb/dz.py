from pymongo import MongoClient
from pprint import pprint
import pandas as pd

# задание 1

client = MongoClient('localhost', 27017)
db = client['vacancies']

hh = db.headhunter
sj = db.superjob

hh_source = pd.read_csv('hh.csv').to_dict('records')
sj_source = pd.read_csv('sj.csv').to_dict('records')

hh.insert_many(hh_source)
sj.insert_many(sj_source)

# задание 2

for line in hh.find(
        {'$or': [{'min_salary': {'$gte': 150000}}, {'max_salary': {'$gte': 150000}}], 'currency': 'руб'},
        {'name': True, 'employer': True, 'location': True, 'min_salary': True, 'max_salary': True, 'currency': True,
         '_id': False}).limit(10):
    pprint(line)

# задание 3
# hh.update_many({}, hh_source, upsert=True)