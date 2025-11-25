import os
from pymongo import MongoClient
from dotenv import load_dotenv
from datetime import datetime, timedelta
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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
            # Test connection with shorter timeout
            Database.client = MongoClient(mongo_uri, serverSelectionTimeoutMS=5000)
            # Get database name from URI or default to vois_ckd
            db_name = mongo_uri.split('/')[-1].split('?')[0] or 'vois_ckd'
            Database.db = Database.client[db_name]
            # Test the connection
            Database.client.admin.command('ping')
            print(f"Connected to MongoDB database: {db_name}")
        except Exception as e:
            logger.error(f"Error connecting to MongoDB: {e}")
            print(f"WARNING: Could not connect to MongoDB. Running in offline mode.")
            print("Please ensure MongoDB is running or update MONGO_URI in .env file.")
            Database.client = None
            Database.db = None

    @staticmethod
    def get_db():
        if Database.db is None:
            Database.initialize()
        return Database.db

    @staticmethod
    def close():
        if Database.client:
            try:
                Database.client.close()
            except Exception as e:
                logger.error(f"Error closing database connection: {e}")


# AI Recommendations Helper Functions
def save_ai_recommendations(username, recommendations_data):
    """Save AI-generated recommendations to patient record"""
    try:
        db = Database.get_db()
        if db is None:
            logger.error("Database connection failed in save_ai_recommendations")
            return False
        # Users are stored in 'users' collection, not 'patients'
        users = db['users']
        
        logger.info(f"Saving AI recommendations for user: {username}")
        
        result = users.update_one(
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
        
        if result.modified_count > 0:
            logger.info(f"Successfully saved recommendations for {username}")
            return True
        else:
            logger.warning(f"No document updated for {username}. User might not exist.")
            return False
    except Exception as e:
        logger.error(f"Error saving AI recommendations: {e}")
        return False


def get_ai_recommendations(username):
    """Retrieve AI recommendations for a patient"""
    try:
        db = Database.get_db()
        if db is None:
            return None
        # Users are stored in 'users' collection, not 'patients'
        users = db['users']
        
        user = users.find_one({'username': username})
        
        if not user:
            logger.warning(f"User not found for username: {username}")
            return None
            
        if 'ai_recommendations' in user:
            recommendations = user['ai_recommendations']
            
            # Check if recommendations are still valid (not expired)
            if 'expires_at' in recommendations:
                expiry = recommendations['expires_at']
                now = datetime.utcnow()
                
                if expiry > now:
                    logger.info(f"Found valid recommendations for {username}")
                    return recommendations.get('data')
                else:
                    logger.warning(f"Recommendations for {username} expired at {expiry}")
            else:
                logger.warning(f"No expiry date found for recommendations of {username}")
        else:
            logger.info(f"No AI recommendations found for {username}")
        
        return None
    except Exception as e:
        logger.error(f"Error getting AI recommendations: {e}")
        return None


def has_valid_ai_recommendations(username):
    """Check if patient has valid (non-expired) AI recommendations"""
    try:
        recommendations = get_ai_recommendations(username)
        return recommendations is not None
    except Exception as e:
        logger.error(f"Error checking AI recommendations validity: {e}")
        return False
