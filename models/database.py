import os
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

class Database:
    client = None
    db = None

    @staticmethod
    def initialize():
        mongo_uri = os.environ.get('MONGO_URI')
        if not mongo_uri:
            # Default to local if not provided, but user should provide it
            mongo_uri = "mongodb://localhost:27017/vois_ckd"
            print("WARNING: MONGO_URI not found. Using default local URI.")
        
        try:
            Database.client = MongoClient(mongo_uri)
            # Get database name from URI or default to vois_ckd
            db_name = mongo_uri.split('/')[-1].split('?')[0] or 'vois_ckd'
            Database.db = Database.client[db_name]
            print(f"Connected to MongoDB database: {db_name}")
        except Exception as e:
            print(f"Error connecting to MongoDB: {e}")

    @staticmethod
    def get_db():
        if Database.db is None:
            Database.initialize()
        return Database.db

    @staticmethod
    def close():
        if Database.client:
            Database.client.close()
