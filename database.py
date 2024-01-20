import os
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure

class MongoDB:
    def __init__(self, database_url, database_name):
        try:
            self.client = MongoClient(database_url)
            self.db = self.client[database_name]
        except ConnectionFailure as e:
            # Handle connection failure (e.g., log the error, raise an exception)
            raise RuntimeError(f"Failed to connect to MongoDB: {e}")

    def get_collection(self, collection_name):
        return self.db[collection_name]

# Use environment variables for sensitive information
MONGO_URI = os.environ.get('MONGO_URI')
db_url = MONGO_URI
db_name = "mabuz"

# Initialize the database connection
try:
    db = MongoDB(db_url, db_name)
    print("MongoDB connection successful.")
except RuntimeError as e:
    print(f"Error: {e}")

