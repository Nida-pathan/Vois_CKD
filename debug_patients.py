from models.database import Database
from models.user import get_all_patients_data, get_all_patients
import os
from dotenv import load_dotenv

load_dotenv()
Database.initialize()

print("--- Debugging Patient IDs ---")

print("\nChecking 'patients_data' collection:")
patients_data = get_all_patients_data()
print(f"Total patients in 'patients_data': {len(patients_data)}")
for p in patients_data:
    print(f"ID: {p.get('_id')}, Patient ID: {p.get('patient_id')}, Username: {p.get('username')}")

print("\nChecking 'users' collection (role='patient'):")
users_patients = get_all_patients()
print(f"Total patients in 'users': {len(users_patients)}")
for p in users_patients:
    print(f"ID: {p.id}, Username: {p.username}, Role: {p.role}")

print("--- End Debug ---")
