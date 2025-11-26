from pymongo import MongoClient
import re

try:
    client = MongoClient('mongodb://localhost:27017/')
    db = client['vois_ckd']
    print("Connected to MongoDB: vois_ckd")
    
    username = 'JOHN'
    
    # Test 1: Exact match
    print(f"\n--- Test 1: Exact match for '{username}' ---")
    query1 = {'patient': username}
    results1 = list(db.appointments.find(query1))
    print(f"Found: {len(results1)}")
    
    # Test 2: Regex match
    print(f"\n--- Test 2: Regex match for '^{username}$' (case-insensitive) ---")
    query2 = {'patient': {'$regex': f'^{username}$', '$options': 'i'}}
    results2 = list(db.appointments.find(query2))
    print(f"Found: {len(results2)}")
    
    # Test 3: Regex match with status
    print(f"\n--- Test 3: Regex match + Status ---")
    query3 = {
        'patient': {'$regex': f'^{username}$', '$options': 'i'},
        'status': {'$in': ['pending', 'confirmed']}
    }
    results3 = list(db.appointments.find(query3))
    print(f"Found: {len(results3)}")

except Exception as e:
    print(f"Error: {e}")
