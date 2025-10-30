from flask_login import UserMixin
from werkzeug.security import generate_password_hash

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

patients_data = {}

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
