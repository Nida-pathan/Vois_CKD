from flask_login import UserMixin
from werkzeug.security import generate_password_hash
from models.ckd_model import ckd_model
import os

class User(UserMixin):
    def __init__(self, id, username, password_hash, role):
        self.id = id
        self.username = username
        self.password_hash = password_hash
        self.role = role
    
    def is_doctor(self):
        return self.role == 'doctor'
    
    def is_patient(self):
        return self.role == 'patient'

users_db = {
    'doctor1': User('1', 'doctor1', generate_password_hash('doctor123'), 'doctor'),
    'patient1': User('2', 'patient1', generate_password_hash('patient123'), 'patient'),
    'admin': User('3', 'admin', generate_password_hash('admin123'), 'doctor'),
}

# Add sample patient data for the 3 patients
sample_patients = [
    {
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
        'anemia': 1
    },
    {
        'patient_id': 'P002',
        'patient_name': 'Mary Johnson',
        'age': 58,
        'gender': 'female',
        'bp_systolic': 130,
        'bp_diastolic': 85,
        'specific_gravity': 1.020,
        'albumin': 0,
        'sugar': 0,
        'red_blood_cells': 1,
        'pus_cell': 0,
        'bacteria': 0,
        'blood_glucose': 95,
        'blood_urea': 25,
        'serum_creatinine': 0.9,
        'sodium': 142,
        'potassium': 4.0,
        'hemoglobin': 13.2,
        'packed_cell_volume': 42,
        'white_blood_cell_count': 6800,
        'red_blood_cell_count': 4.8,
        'hypertension': 0,
        'diabetes_mellitus': 0,
        'coronary_artery_disease': 0,
        'appetite': 1,
        'pedal_edema': 0,
        'anemia': 0
    },
    {
        'patient_id': 'P003',
        'patient_name': 'Robert Davis',
        'age': 72,
        'gender': 'male',
        'bp_systolic': 160,
        'bp_diastolic': 95,
        'specific_gravity': 1.010,
        'albumin': 4,
        'sugar': 3,
        'red_blood_cells': 1,
        'pus_cell': 2,
        'bacteria': 1,
        'blood_glucose': 180,
        'blood_urea': 95,
        'serum_creatinine': 3.2,
        'sodium': 135,
        'potassium': 5.1,
        'hemoglobin': 9.8,
        'packed_cell_volume': 32,
        'white_blood_cell_count': 12000,
        'red_blood_cell_count': 3.5,
        'hypertension': 1,
        'diabetes_mellitus': 1,
        'coronary_artery_disease': 1,
        'appetite': 0,
        'pedal_edema': 1,
        'anemia': 1
    }
]

# Process the sample patients with the CKD model to generate predictions
patients_data = {}
for patient in sample_patients:
    # Only process if not on Vercel to save build time
    if not os.environ.get('VERCEL'):
        prediction = ckd_model.predict_risk(patient)
        patient.update(prediction)
    patients_data[patient['patient_id']] = patient

patient_records = {
    'patient1': {
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
            },
            {
                'date': '2025-08-01',
                'serum_creatinine': 1.2,
                'blood_urea': 40,
                'egfr': 68,
                'hemoglobin': 12.1,
                'bp_systolic': 138,
                'bp_diastolic': 88
            }
        ]
    }
}