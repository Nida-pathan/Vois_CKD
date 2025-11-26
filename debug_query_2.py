from pymongo import MongoClient
import re

try:
    client = MongoClient('mongodb://localhost:27017/')
    db = client['vois']
    print("Connected to MongoDB: vois")
    
    username = 'JOHN'
    
    # Test 4: Python Regex Object
    print(f"\n--- Test 4: Python Regex Object ---")
    regex = re.compile(f'^{re.escape(username)}$', re.IGNORECASE)
    query4 = {'patient': regex}
    results4 = list(db.appointments.find(query4))
    print(f"Found: {len(results4)}")
    
    # Test 5: $regex without $options (inline flags)
    print(f"\n--- Test 5: Inline flags ---")
    query5 = {'patient': {'$regex': f'(?i)^{username}$'}}
    results5 = list(db.appointments.find(query5))
    print(f"Found: {len(results5)}")

except Exception as e:
    print(f"Error: {e}")
