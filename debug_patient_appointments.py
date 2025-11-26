
import sys
import os
sys.path.append(os.getcwd())
from models.database import Database
from models.user import get_appointments_for_patient

# Initialize DB
Database.initialize()
db = Database.get_db()

if db is None:
    print("Database connection failed")
    sys.exit(1)

print("--- Testing get_appointments_for_patient('john') ---", flush=True)
upcoming = get_appointments_for_patient('john')
print(f"Found {len(upcoming)} appointments for john", flush=True)

for i, apt in enumerate(upcoming):
    print(f"Appointment {i+1}:", flush=True)
    print(f"  Doctor: {apt.get('doctor')}", flush=True)
    print(f"  Meet Link: '{apt.get('meet_link')}'", flush=True)
    print(f"  Status: {apt.get('status')}", flush=True)
    print("-" * 20, flush=True)

print("\n--- Testing get_appointments_for_patient('Aditya21') ---", flush=True)
upcoming_aditya = get_appointments_for_patient('Aditya21')
print(f"Found {len(upcoming_aditya)} appointments for Aditya21", flush=True)

for i, apt in enumerate(upcoming_aditya):
    print(f"Appointment {i+1}:", flush=True)
    print(f"  Doctor: {apt.get('doctor')}", flush=True)
    print(f"  Meet Link: '{apt.get('meet_link')}'", flush=True)
    print(f"  Status: {apt.get('status')}", flush=True)
    print("-" * 20, flush=True)
