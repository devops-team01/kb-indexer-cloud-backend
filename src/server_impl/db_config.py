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

    # Dummy environment variables
    env_vars = [
        {"name": "DATA_DIR", "value": "/app/data"},
        {"name": "ELASTICSEARCH_HOST", "value": "https://host:PORT/path/"},
        {"name": "ELASTICSEARCH_USERNAME", "value": "<es username>"},
        {"name": "ELASTICSEARCH_PASSWORD", "value": "<es password>"},
        {"name": "KAGGLE_USERNAME", "value": "<A Kaggle username>"},
        {"name": "KAGGLE_KEY", "value": "<A Kaggle API key>"},
        {"name": "GITHUB_API_TOKEN", "value": "<A GitHub API token>"}
    ]

    # Truncate environment_variables collection
    db.environment_variables.delete_many({}) # TODO change this in production
    db.environment_variables.insert_many(env_vars)
