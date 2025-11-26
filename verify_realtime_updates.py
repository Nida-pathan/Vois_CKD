from models.database import Database
from models.user import User, get_doctor_patients_with_details, update_patient_lab_values
import datetime
import time

# Initialize DB
Database.initialize()

def verify_realtime_updates():
    print("Verifying Real-Time Updates Logic...")
    
    # 1. Pick a test patient
    test_patient_username = 'Jack'
    print(f"Test Patient: {test_patient_username}")
    
    # 2. Get initial state for a doctor (simulated)
    # We need a doctor username. Let's assume 'dr_smith' or similar exists, 
    # or just use the helper directly if we assume the patient is assigned.
    # For this test, we'll just check if the helper returns the patient and what the date is.
    
    # Create a dummy doctor if needed or just rely on the fact that the helper 
    # filters by appointments. 
    # To make this robust, let's just check the helper's logic for a specific doctor 
    # if we know one, OR just check the patient record update part which is the core.
    
    # Let's simulate the doctor 'dr_smith' who has an appointment with 'Jack'
    # We might need to ensure this relationship exists in the DB for the helper to return it.
    # Alternatively, we can just verify that get_doctor_patients_with_details returns 
    # the correct data structure when it DOES find the patient.
    
    # Let's try to find a doctor who has this patient.
    db = Database.get_db()
    appointment = db.appointments.find_one({'patient': test_patient_username})
    doctor_username = appointment['doctor'] if appointment else None
    
    if not doctor_username:
        print("No appointment found for Jack. Creating a dummy appointment for testing.")
        doctor_username = 'test_doctor'
        db.appointments.insert_one({
            'doctor': doctor_username,
            'patient': test_patient_username,
            'date': '2025-01-01',
            'time': '10:00',
            'status': 'confirmed'
        })
        
    print(f"Using Doctor: {doctor_username}")
    
    # 3. Fetch initial data
    print("Fetching initial data...")
    patients_before = get_doctor_patients_with_details(doctor_username)
    target_patient_before = next((p for p in patients_before if p['username'] == test_patient_username), None)
    
    if target_patient_before:
        print(f"Initial Last Updated: {target_patient_before['last_updated']}")
    else:
        print("Patient not found in doctor's list initially.")

    # 4. Update patient data (Simulate Lab Upload)
    print("\nSimulating Lab Upload...")
    new_lab_values = {
        'egfr': 60,
        'serum_creatinine': 1.2,
        'test_date': datetime.datetime.now()
    }
    # Pass a dummy prediction string
    update_patient_lab_values(test_patient_username, new_lab_values, "Stage 2 CKD")
    
    # 5. Fetch data again
    print("Fetching updated data...")
    patients_after = get_doctor_patients_with_details(doctor_username)
    target_patient_after = next((p for p in patients_after if p['username'] == test_patient_username), None)
    
    if target_patient_after:
        print(f"New Last Updated: {target_patient_after['last_updated']}")
        
        if target_patient_before and target_patient_after['last_updated'] != target_patient_before['last_updated']:
            print("SUCCESS: Last Updated field changed!")
        elif not target_patient_before:
             print("SUCCESS: Patient appeared in the list!")
        else:
            print("WARNING: Last Updated field did NOT change (might be too fast or same minute).")
    else:
        print("FAILURE: Patient not found in doctor's list after update.")

if __name__ == "__main__":
    verify_realtime_updates()
