from pymongo import MongoClient

client = MongoClient('mongodb://mongodb:27017/')
db = client['kb_indexer_db']

def insert_initial_values(db):
    indexers = ["api", "web", "notebook", "dataset"]
    db.indexers.delete_many({}) # Truncate
    for i in indexers:
        try:
            db.indexers.insert_one({'type': i, '_id': i})
        except Exception as e:
            print(e)
