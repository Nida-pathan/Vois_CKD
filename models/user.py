from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from models.database import Database
from bson.objectid import ObjectId
import pandas as pd
import datetime

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
        """Get user by ID with error handling"""
        try:
            db = Database.get_db()
            if db is None:
                return None
            user_data = db.users.find_one({'_id': ObjectId(user_id)})
            if user_data:
                return User(user_data)
        except:
            pass
        return None

    @staticmethod
    def get_by_username(username):
        """Get user by username with error handling"""
        try:
            db = Database.get_db()
            if db is None:
                return None
            user_data = db.users.find_one({'username': username})
            if user_data:
                return User(user_data)
            return None
        except Exception as e:
            print(f"Error getting user by username {username}: {e}")
            return None

    @staticmethod
    def create_user(username, password, role, email=None, specialization=None):
        """Create user with error handling"""
        try:
            db = Database.get_db()
            if db is None:
                return None
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
        except Exception as e:
            print(f"Error creating user {username}: {e}")
            return None

# --- Helper functions for Data Persistence ---

def get_all_doctors():
    """Get all doctors with error handling"""
    try:
        db = Database.get_db()
        if db is None:
            return []
        doctors_cursor = db.users.find({'role': 'doctor'})
        return [User(doc) for doc in doctors_cursor]
    except Exception as e:
        print(f"Error getting doctors: {e}")
        return []

def get_all_patients():
    """Get all patients with error handling"""
    try:
        db = Database.get_db()
        if db is None:
            return []
        patients_cursor = db.users.find({'role': 'patient'})
        return [User(pat) for pat in patients_cursor]
    except Exception as e:
        print(f"Error getting patients: {e}")
        return []

# Patient Data (Medical Records/Risk Analysis)
def get_patient_data(patient_id):
    """Get patient data with error handling"""
    try:
        db = Database.get_db()
        if db is None:
            return None
        return db.patients_data.find_one({'patient_id': patient_id})
    except Exception as e:
        print(f"Error getting patient data for {patient_id}: {e}")
        return None

def save_patient_data(patient_data):
    """Save patient data with error handling"""
    try:
        db = Database.get_db()
        if db is None:
            return
        # Upsert based on patient_id
        db.patients_data.update_one(
            {'patient_id': patient_data['patient_id']},
            {'$set': patient_data},
            upsert=True
        )
    except Exception as e:
        print(f"Error saving patient data: {e}")

def get_all_patients_data():
    db = Database.get_db()
    return list(db.patients_data.find())

# Patient Records (Historical/Trends)
def get_patient_records(username):
    """Get patient records with error handling"""
    try:
        db = Database.get_db()
        if db is None:
            return {}
        record = db.patient_records.find_one({'username': username})
        return record if record else {}
    except Exception as e:
        print(f"Error getting patient records for {username}: {e}")
        return {}

def save_patient_record(username, data):
    """Save patient record with error handling"""
    try:
        db = Database.get_db()
        if db is None:
            return
        db.patient_records.update_one(
            {'username': username},
            {'$set': data},
            upsert=True
        )
    except Exception as e:
        print(f"Error saving patient record for {username}: {e}")

# Patient Upload Trials
def get_patient_trials(username):
    """Get patient trials with error handling"""
    try:
        db = Database.get_db()
        if db is None:
            # Default trial info
            return {'username': username, 'remaining': 999, 'used': 0}
        trial = db.patient_trials.find_one({'username': username})
        if trial:
            return trial
        # Default trial info
        return {'username': username, 'remaining': 999, 'used': 0}
    except Exception as e:
        print(f"Error getting patient trials for {username}: {e}")
        # Default trial info
        return {'username': username, 'remaining': 999, 'used': 0}

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

def update_patient_lab_values(username, lab_values, prediction):
    """Update patient lab values and history"""
    db = Database.get_db()
    
    # Get existing record to preserve other fields
    record = db.patient_records.find_one({'username': username})
    if not record:
        record = {'username': username, 'history': []}
    
    # Update current metrics
    current_metrics = record.get('current_metrics', {})
    # Merge new values
    for k, v in lab_values.items():
        if v is not None:
            current_metrics[k] = v
            
    # Add prediction info to metrics for easy access
    if prediction:
        current_metrics['disease_prediction'] = prediction
            
    # Create history entry
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    history_entry = {
        'date': timestamp,
        'metrics': lab_values,
        'prediction': prediction
    }
    
    # Update database
    db.patient_records.update_one(
        {'username': username},
        {
            '$set': {'current_metrics': current_metrics},
            '$push': {'history': history_entry}
        },
        upsert=True
    )

def decrement_trial_count(username):
    """Deprecated: No longer enforcing trial limits"""
    pass