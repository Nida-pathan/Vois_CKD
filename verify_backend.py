import os
import sys
from flask import Flask
from models.database import Database
from models.user import User, save_patient_data, get_patient_data, create_appointment, get_appointments_for_doctor
import pandas as pd

# Setup Flask app context
app = Flask(__name__)
app.config['SECRET_KEY'] = 'test_secret'

# Initialize DB
Database.initialize()

def test_user_creation():
    print("\n--- Testing User Creation ---")
    username = "test_doctor_verify"
    password = "password123"
    
    # Clean up if exists
    db = Database.get_db()
    db.users.delete_one({'username': username})
    
    user = User.create_user(username, password, 'doctor', 'test@example.com', 'Nephrology')
    if user:
        print(f"SUCCESS: Created user {user.username} with ID {user.id}")
    else:
        print("FAILURE: Could not create user")
        return False
        
    # Verify retrieval
    retrieved_user = User.get_by_username(username)
    if retrieved_user and retrieved_user.id == user.id:
        print(f"SUCCESS: Retrieved user {retrieved_user.username}")
    else:
        print("FAILURE: Could not retrieve user")
        return False
    return True

def test_patient_data_persistence():
    print("\n--- Testing Patient Data Persistence ---")
    patient_id = "TEST_PATIENT_001"
    
    # Clean up
    db = Database.get_db()
    db.patients_data.delete_one({'patient_id': patient_id})
    
    data = {
        'patient_id': patient_id,
        'patient_name': 'Test Patient',
        'age': 45,
        'risk_percentage': 25,
        'stage': 2
    }
    
    save_patient_data(data)
    print(f"Saved patient data for {patient_id}")
    
    retrieved = get_patient_data(patient_id)
    if retrieved and retrieved['patient_name'] == 'Test Patient':
        print(f"SUCCESS: Retrieved patient data: {retrieved['patient_name']}")
    else:
        print("FAILURE: Could not retrieve patient data")
        return False
    return True

def test_appointment_creation():
    print("\n--- Testing Appointment Creation ---")
    appointment = {
        'patient': 'test_patient_user',
        'doctor': 'test_doctor_verify',
        'preferred_date': '2025-12-01',
        'status': 'pending'
    }
    
    appt_id = create_appointment(appointment)
    print(f"Created appointment with ID {appt_id}")
    
    appts = get_appointments_for_doctor('test_doctor_verify')
    if len(appts) > 0:
        print(f"SUCCESS: Found {len(appts)} appointments for doctor")
    else:
        print("FAILURE: No appointments found")
        return False
    return True

if __name__ == "__main__":
    print("Starting Backend Verification...")
    try:
        if test_user_creation() and test_patient_data_persistence() and test_appointment_creation():
            print("\nALL TESTS PASSED!")
        else:
            print("\nSOME TESTS FAILED.")
    except Exception as e:
        print(f"\nEXCEPTION OCCURRED: {e}")
        import traceback
        traceback.print_exc()
