from pymongo import MongoClient
from models import Indexer

client = MongoClient('mongodb://mongodb:27017/')
db = client['kb_indexer_db']

def insert_initial_values(db):
    indexers = ["api", "web", "notebook", "dataset"]
    for i in indexers:
        db.indexers.insert_one({type: i})
