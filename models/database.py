import os
from pymongo import MongoClient
from dotenv import load_dotenv
from datetime import datetime, timedelta

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


# AI Recommendations Helper Functions
def save_ai_recommendations(username, recommendations_data):
    """Save AI-generated recommendations to patient record"""
    db = Database.get_db()
    patients = db['patients']
    
    patients.update_one(
        {'username': username},
        {
            '$set': {
                'ai_recommendations': {
                    'generated_at': datetime.utcnow(),
                    'expires_at': datetime.utcnow() + timedelta(days=30),
                    'data': recommendations_data
                }
            }
        }
    )
    return True


def get_ai_recommendations(username):
    """Retrieve AI recommendations for a patient"""
    db = Database.get_db()
    patients = db['patients']
    
    patient = patients.find_one({'username': username})
    if patient and 'ai_recommendations' in patient:
        recommendations = patient['ai_recommendations']
        
        # Check if recommendations are still valid (not expired)
        if 'expires_at' in recommendations:
            if recommendations['expires_at'] > datetime.utcnow():
                return recommendations.get('data')
    
    return None


def has_valid_ai_recommendations(username):
    """Check if patient has valid (non-expired) AI recommendations"""
    recommendations = get_ai_recommendations(username)
    return recommendations is not None
