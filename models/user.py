from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from models.database import Database
from bson.objectid import ObjectId
import pandas as pd

class User(UserMixin):
    def __init__(self, user_data):
        self.id = str(user_data.get('_id'))
        self.username = user_data.get('username')
        self.password_hash = user_data.get('password_hash')
        self.role = user_data.get('role')
        self.email = user_data.get('email')
        self.specialization = user_data.get('specialization')
        # For doctors: list of patient IDs they manage
        self.patients = user_data.get('patients', []) 

    def is_doctor(self):
        return self.role == 'doctor'
    
    def is_patient(self):
        return self.role == 'patient'

    @staticmethod
    def get_by_id(user_id):
        db = Database.get_db()
        try:
            user_data = db.users.find_one({'_id': ObjectId(user_id)})
            if user_data:
                return User(user_data)
        except:
            pass
        return None

    @staticmethod
    def get_by_username(username):
        db = Database.get_db()
        user_data = db.users.find_one({'username': username})
        if user_data:
            return User(user_data)
        return None

    @staticmethod
    def create_user(username, password, role, email=None, specialization=None):
        db = Database.get_db()
        if db.users.find_one({'username': username}):
            return None
        
        user_data = {
            'username': username,
            'password_hash': generate_password_hash(password),
            'role': role,
            'email': email,
            'specialization': specialization,
            'created_at': pd.Timestamp.now().isoformat(),
            'patients': [] # Initialize empty patient list
        }
        
        result = db.users.insert_one(user_data)
        user_data['_id'] = result.inserted_id
        return User(user_data)

# --- Helper functions for Data Persistence ---

def get_all_doctors():
    db = Database.get_db()
    doctors_cursor = db.users.find({'role': 'doctor'})
    return [User(doc) for doc in doctors_cursor]

def get_all_patients():
    db = Database.get_db()
    patients_cursor = db.users.find({'role': 'patient'})
    return [User(pat) for pat in patients_cursor]

# Patient Data (Medical Records/Risk Analysis)
def get_patient_data(patient_id):
    db = Database.get_db()
    return db.patients_data.find_one({'patient_id': patient_id})

def save_patient_data(patient_data):
    db = Database.get_db()
    # Upsert based on patient_id
    db.patients_data.update_one(
        {'patient_id': patient_data['patient_id']},
        {'$set': patient_data},
        upsert=True
    )

def get_all_patients_data():
    db = Database.get_db()
    return list(db.patients_data.find())

# Patient Records (Historical/Trends)
def get_patient_records(username):
    db = Database.get_db()
    record = db.patient_records.find_one({'username': username})
    return record if record else {}

def save_patient_record(username, data):
    db = Database.get_db()
    db.patient_records.update_one(
        {'username': username},
        {'$set': data},
        upsert=True
    )

# Patient Upload Trials
def get_patient_trials(username):
    db = Database.get_db()
    trial = db.patient_trials.find_one({'username': username})
    if trial:
        return trial
    # Default trial info
    return {'username': username, 'remaining': 2, 'used': 0}

def update_patient_trials(username, remaining, used):
    db = Database.get_db()
    db.patient_trials.update_one(
        {'username': username},
        {'$set': {'remaining': remaining, 'used': used}},
        upsert=True
    )

# Appointments
def create_appointment(appointment_data):
    db = Database.get_db()
    result = db.appointments.insert_one(appointment_data)
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from models.database import Database
from bson.objectid import ObjectId
import pandas as pd

class User(UserMixin):
    def __init__(self, user_data):
        self.id = str(user_data.get('_id'))
        self.username = user_data.get('username')
        self.password_hash = user_data.get('password_hash')
        self.role = user_data.get('role')
        self.email = user_data.get('email')
        self.specialization = user_data.get('specialization')
        # For doctors: list of patient IDs they manage
        self.patients = user_data.get('patients', []) 

    def is_doctor(self):
        return self.role == 'doctor'
    
    def is_patient(self):
        return self.role == 'patient'

    @staticmethod
    def get_by_id(user_id):
        db = Database.get_db()
        try:
            user_data = db.users.find_one({'_id': ObjectId(user_id)})
            if user_data:
                return User(user_data)
        except:
            pass
        return None

    @staticmethod
    def get_by_username(username):
        db = Database.get_db()
        user_data = db.users.find_one({'username': username})
        if user_data:
            return User(user_data)
        return None

    @staticmethod
    def create_user(username, password, role, email=None, specialization=None):
        db = Database.get_db()
        if db.users.find_one({'username': username}):
            return None
        
        user_data = {
            'username': username,
            'password_hash': generate_password_hash(password),
            'role': role,
            'email': email,
            'specialization': specialization,
            'created_at': pd.Timestamp.now().isoformat(),
            'patients': [] # Initialize empty patient list
        }
        
        result = db.users.insert_one(user_data)
        user_data['_id'] = result.inserted_id
        return User(user_data)

# --- Helper functions for Data Persistence ---

def get_all_doctors():
    db = Database.get_db()
    doctors_cursor = db.users.find({'role': 'doctor'})
    return [User(doc) for doc in doctors_cursor]

def get_all_patients():
    db = Database.get_db()
    patients_cursor = db.users.find({'role': 'patient'})
    return [User(pat) for pat in patients_cursor]

# Patient Data (Medical Records/Risk Analysis)
def get_patient_data(patient_id):
    db = Database.get_db()
    return db.patients_data.find_one({'patient_id': patient_id})

def save_patient_data(patient_data):
    db = Database.get_db()
    # Upsert based on patient_id
    db.patients_data.update_one(
        {'patient_id': patient_data['patient_id']},
        {'$set': patient_data},
        upsert=True
    )

def get_all_patients_data():
    db = Database.get_db()
    return list(db.patients_data.find())

# Patient Records (Historical/Trends)
def get_patient_records(username):
    db = Database.get_db()
    record = db.patient_records.find_one({'username': username})
    return record if record else {}

def save_patient_record(username, data):
    db = Database.get_db()
    db.patient_records.update_one(
        {'username': username},
        {'$set': data},
        upsert=True
    )

# Patient Upload Trials
def get_patient_trials(username):
    db = Database.get_db()
    trial = db.patient_trials.find_one({'username': username})
    if trial:
        return trial
    # Default trial info
    return {'username': username, 'remaining': 2, 'used': 0}

def update_patient_trials(username, remaining, used):
    db = Database.get_db()
    db.patient_trials.update_one(
        {'username': username},
        {'$set': {'remaining': remaining, 'used': used}},
        upsert=True
    )

# Appointments
def create_appointment(appointment_data):
    db = Database.get_db()
    result = db.appointments.insert_one(appointment_data)
    return str(result.inserted_id)

def get_appointments_for_doctor(doctor_name):
    db = Database.get_db()
    return list(db.appointments.find({'doctor': doctor_name}))

def get_appointments_for_patient(patient_username):
    db = Database.get_db()
    return list(db.appointments.find({'patient': patient_username}))

def save_feedback(feedback_data):
    db = Database.get_db()
    db.feedbacks.insert_one(feedback_data)

def get_all_feedbacks():
    db = Database.get_db()
    return list(db.feedbacks.find())