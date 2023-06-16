import pymongo

try:
    mongo_client = pymongo.MongoClient(
        host="localhost",
        port=27017
    )
except:
    print("Cannot connect to mongodb")

db = mongo_client.Synin

from .models import *
