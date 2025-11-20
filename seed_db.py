from models.database import Database
from models.user import User, save_patient_data, save_patient_record
from werkzeug.security import generate_password_hash
import pandas as pd
import os

def seed_database():
    print("Seeding database...")
    
    # Initialize DB
    if not os.environ.get('MONGO_URI'):
        print("MONGO_URI not set. Using default: mongodb://localhost:27017/vois_ckd")
    Database.initialize()
    db = Database.get_db()
    
    # Clear existing data (optional, be careful in production)
    # db.users.delete_many({})
    # db.patients_data.delete_many({})
    # db.patient_records.delete_many({})
    
    # Create Admin
    if not User.get_by_username('admin'):
        User.create_user('admin', 'admin123', 'doctor', 'admin@vois.com', 'Administrator')
        print("Created admin user")
        
    # Create Doctor
    if not User.get_by_username('doctor1'):
        User.create_user('doctor1', 'doctor123', 'doctor', 'doctor1@vois.com', 'Nephrologist')
        print("Created doctor1 user")
        
    # Create Patient
    if not User.get_by_username('patient1'):
        User.create_user('patient1', 'patient123', 'patient', 'patient1@vois.com')
        print("Created patient1 user")
        
    # Add Sample Patient Data (Risk Prediction)
    sample_patient_data = {
        'patient_id': 'P001',
        'patient_name': 'John Smith',
        'age': 65,
        'gender': 'male',
        'bp_systolic': 145,
        'bp_diastolic': 92,
        'specific_gravity': 1.015,
        'albumin': 2,
        'sugar': 1,
        'red_blood_cells': 1,
        'pus_cell': 0,
        'bacteria': 0,
        'blood_glucose': 110,
        'blood_urea': 55,
        'serum_creatinine': 1.8,
        'sodium': 138,
        'potassium': 4.2,
        'hemoglobin': 11.5,
        'packed_cell_volume': 38,
        'white_blood_cell_count': 7500,
        'red_blood_cell_count': 4.2,
        'hypertension': 1,
        'diabetes_mellitus': 1,
        'coronary_artery_disease': 0,
        'appetite': 1,
        'pedal_edema': 0,
        'anemia': 1,
        'risk_percentage': 85,
        'stage': 3,
        'risk_level': 'High'
    }
    save_patient_data(sample_patient_data)
    print("Added sample patient data")
    
    # Add Sample Patient Record (History)
    sample_history = {
        'username': 'patient1',
        'name': 'John Doe',
        'age': 55,
        'gender': 'male',
        'patient_id': 'P001',
        'history': [
            {
                'date': '2025-10-01',
                'serum_creatinine': 1.5,
                'blood_urea': 45,
                'egfr': 58,
                'hemoglobin': 11.2,
                'bp_systolic': 145,
                'bp_diastolic': 92
            },
            {
                'date': '2025-09-01',
                'serum_creatinine': 1.3,
                'blood_urea': 42,
                'egfr': 62,
                'hemoglobin': 11.8,
                'bp_systolic': 142,
                'bp_diastolic': 90
            }
        ]
    }
    save_patient_record('patient1', sample_history)
    print("Added sample patient history")
    
    print("Database seeding completed!")

if __name__ == "__main__":
    seed_database()
