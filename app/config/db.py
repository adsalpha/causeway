from pymongo import MongoClient
from collections import OrderedDict


client = MongoClient('127.0.0.1', 27017, document_class=OrderedDict)
db = client['rein']
jobs = db['jobs']
users = db['users']
requests = db['requests']
