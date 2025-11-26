from pymongo import MongoClient

try:
    client = MongoClient('mongodb://localhost:27017/')
    print("Connected to MongoDB")
    print(f"Databases: {client.list_database_names()}")
    
    db = client['vois_ckd']
    print("Connected to MongoDB: vois_ckd")
    
    appointments = list(db.appointments.find())
    print(f"Total appointments: {len(appointments)}")
    
    for apt in appointments:
        patient = apt.get('patient')
        print(f"ID: {apt.get('_id')}")
        print(f"Patient (repr): {repr(patient)}")
        print(f"Patient (len): {len(patient) if patient else 'None'}")
        print("-" * 20)

except Exception as e:
    print(f"Error: {e}")
