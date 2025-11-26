import sys
import os
sys.path.append(os.getcwd())
from models.database import Database
import pandas as pd

def debug_appointments():
    try:
        db = Database.get_db()
        if db is None:
            print("Failed to connect to database")
            return

        print("\n--- APPOINTMENTS FOR JOHN ---", flush=True)
        appointments = list(db.appointments.find())
        count = 0
        for apt in appointments:
            patient = apt.get('patient', '')
            if 'john' in str(patient).lower():
                print(f"STATUS: '{apt.get('status')}'", flush=True)
                print(f"Patient: '{patient}' | Doctor: '{apt.get('doctor')}'", flush=True)
                print(f"Meet Link: {apt.get('meet_link')}", flush=True)
                print("-" * 30, flush=True)
                count += 1
        print(f"Found {count} appointments for 'john'", flush=True)
            
        print(f"\nTotal Appointments: {len(appointments)}")

        print("\n--- ALL USERS (Doctors) ---")
        doctors = list(db.users.find({'role': 'doctor'}))
        for doc in doctors:
            print(f"Username: {doc.get('username')}")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    debug_appointments()
