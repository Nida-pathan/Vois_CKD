from models.database import Database
from models.user import User, get_patient_records, get_all_patients_data
import datetime

# Initialize DB
Database.initialize()

def verify_last_updated():
    print("Verifying Last Updated Logic...")
    
    from models.user import get_all_patients
    patients = get_all_patients()
    print(f"Found {len(patients)} patients in users collection.")
    
    for user in patients:
        username = user.username
        print(f"\nChecking patient: {username}")
        
        # Mimic the logic in doctor_dashboard
        records = get_patient_records(username)
        last_updated = 'N/A'
        
        if records and 'history' in records and records['history']:
            latest_entry = records['history'][-1]
            last_updated = latest_entry.get('date', 'N/A')
            print(f"  Found history. Latest entry date: {last_updated}")
        else:
            print("  No history found.")
            
        if last_updated == 'N/A':
            if hasattr(user, 'created_at'):
                last_updated = user.created_at
                print(f"  Using user.created_at: {last_updated}")
                
        print(f"  FINAL Last Updated: {last_updated}")

if __name__ == "__main__":
    verify_last_updated()
