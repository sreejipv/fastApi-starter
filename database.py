from pymongo import MongoClient

class MongoDB:
    def __init__(self, database_url, database_name):
        self.client = MongoClient(database_url)
        self.db = self.client[database_name]

    def get_collection(self, collection_name):
        return self.db[collection_name]

# Initialize the database connection
db = MongoDB("mongodb://localhost:27017/", "mabuz")
