from pymongo import MongoClient

try:
    client = MongoClient('mongodb://localhost:27017/')
    print("Connected to MongoDB")
    
    dbs = client.list_database_names()
    print(f"Databases: {dbs}")
    
    for db_name in ['vois', 'vois_ckd']:
        if db_name in dbs:
            print(f"\n--- Checking DB: {db_name} ---")
            db = client[db_name]
            appointments = list(db.appointments.find())
            print(f"Total appointments in {db_name}: {len(appointments)}")
            for apt in appointments:
                print(f"ID: {apt.get('_id')}, Patient: '{apt.get('patient')}', Status: '{apt.get('status')}'")
        else:
            print(f"\nDB {db_name} does not exist.")

except Exception as e:
    print(f"Error: {e}")
