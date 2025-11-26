import sys
import os
sys.path.append(os.getcwd())
from models.user import get_appointments_for_patient

def trigger_fix():
    print("Fetching appointments for JOHN to trigger link generation...")
    appointments = get_appointments_for_patient('JOHN')
    print(f"Found {len(appointments)} appointments.")
    for apt in appointments:
        print(f"Doctor: {apt.get('doctor')} | Meet Link: {apt.get('meet_link')}")

if __name__ == "__main__":
    trigger_fix()
