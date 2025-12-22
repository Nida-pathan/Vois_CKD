#!/usr/bin/env python3
"""
Script to reset the tour status for a specific user in the CKD Companion application.
This will allow the welcome tour to be shown again for that user.
"""

import sys
import os

# Add the project root to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__)))

from models.database import Database
from bson.objectid import ObjectId

def reset_tour_status(username):
    """
    Reset the tour status for a specific user.
    
    Args:
        username (str): The username whose tour status should be reset
    """
    try:
        # Initialize database connection
        Database.initialize()
        db = Database.get_db()
        
        if db is None:
            print("Error: Could not connect to database")
            return False
            
        # Find the user by username
        user = db.users.find_one({"username": username})
        
        if not user:
            print(f"Error: User '{username}' not found")
            return False
            
        # Reset the has_seen_tour field
        result = db.users.update_one(
            {"_id": user["_id"]},
            {"$unset": {"has_seen_tour": ""}}
        )
        
        if result.modified_count > 0:
            print(f"Successfully reset tour status for user '{username}'")
            return True
        else:
            print(f"No changes made for user '{username}' (may already be reset)")
            return True
            
    except Exception as e:
        print(f"Error resetting tour status: {str(e)}")
        return False

def main():
    """Main function to run the script."""
    if len(sys.argv) != 2:
        print("Usage: python reset_tour_status.py <username>")
        print("Example: python reset_tour_status.py ar3")
        sys.exit(1)
        
    username = sys.argv[1]
    print(f"Resetting tour status for user: {username}")
    
    success = reset_tour_status(username)
    
    if success:
        print("Operation completed successfully")
        sys.exit(0)
    else:
        print("Operation failed")
        sys.exit(1)

if __name__ == "__main__":
    main()