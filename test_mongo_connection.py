from models.database import Database
import os

def test_connection():
    print("Testing MongoDB connection...")
    # Ensure MONGO_URI is set or use default
    if not os.environ.get('MONGO_URI'):
        print("MONGO_URI not set. Using default: mongodb://localhost:27017/vois_ckd")
    
    Database.initialize()
    db = Database.get_db()
    
    try:
        # Ping the database
        db.command('ping')
        print("Successfully connected to MongoDB!")
        
        # List collections
        collections = db.list_collection_names()
        print(f"Collections: {collections}")
        
    except Exception as e:
        print(f"Failed to connect to MongoDB: {e}")

if __name__ == "__main__":
    test_connection()
