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
        self.city = user_data.get('city')
        # For doctors: list of patient IDs they manage
        self.patients = user_data.get('patients', []) 
        self.has_seen_tour = user_data.get('has_seen_tour', False)

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
    def create_user(username, password, role, email=None, specialization=None, city=None):
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
                'city': city,
                'created_at': pd.Timestamp.now().isoformat(),
                'patients': [], # Initialize empty patient list
                'has_seen_tour': False
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

def complete_appointment(appointment_id):
    """Mark an appointment as completed"""
    try:
        db = Database.get_db()
        from bson import ObjectId
        result = db.appointments.update_one(
            {'_id': ObjectId(appointment_id)},
            {'$set': {'status': 'completed'}}
        )
        return result.modified_count > 0
    except Exception as e:
        print(f"Error completing appointment {appointment_id}: {e}")
        return False

def get_appointments_for_doctor(doctor_name):
    db = Database.get_db()
    if db is None:
        return []
        
    appointments = list(db.appointments.find({'doctor': doctor_name}))
    
    # Generate meet link if missing for any appointment
    for apt in appointments:
        if not apt.get('meet_link'):
            import uuid
            room_id = f"ckd-appointment-{uuid.uuid4()}"
            meet_link = f"https://meet.jit.si/{room_id}"
            apt['meet_link'] = meet_link
            # Update DB
            db.appointments.update_one(
                {'_id': apt['_id']},
                {'$set': {'meet_link': meet_link}}
            )
            
    # Sort by date and time
    appointments.sort(key=lambda x: (x.get('preferred_date', ''), x.get('preferred_time', '')))
    
    return appointments

def get_appointments_for_patient(patient_username):
    """Get upcoming appointments for a patient with doctor details"""
    try:
        db = Database.get_db()
        if db is None:
            return []
        
        # DEBUG LOGGING
        print(f"\n--- get_appointments_for_patient ---")
        print(f"DB Name: {db.name}")
        print(f"Querying for: '{patient_username}'")
        
        # Try multiple query approaches to find appointments
        query_options = [
            {'patient': patient_username},  # Exact match
            {'patient': {'$regex': f'^{patient_username}$', '$options': 'i'}},  # Case insensitive exact match
        ]
        
        appointments = []
        for query in query_options:
            appointments = list(db.appointments.find(query))
            if appointments:
                print(f"Found {len(appointments)} appointments with query: {query}")
                break
        
        if not appointments:
            # If no appointments found, let's check what appointments exist in the database
            all_appointments = list(db.appointments.find())
            print(f"Total appointments in DB: {len(all_appointments)}")
            for apt in all_appointments[:5]:  # Show first 5
                print(f"  Appointment: patient='{apt.get('patient')}', doctor='{apt.get('doctor')}'")
        
        # Filter for pending/confirmed status and future dates
        from datetime import datetime
        today = datetime.now().date()
        filtered_appointments = []
        for apt in appointments:
            # Check status
            if apt.get('status') not in ['pending', 'confirmed']:
                continue
            
            # Check date (if it's in the future or today)
            try:
                apt_date_str = apt.get('preferred_date', '')
                if apt_date_str:
                    apt_date = datetime.strptime(apt_date_str, '%Y-%m-%d').date()
                    if apt_date >= today:
                        filtered_appointments.append(apt)
            except ValueError:
                # If date parsing fails, include it to be safe
                filtered_appointments.append(apt)
        
        print(f"Filtered appointments (future/pending): {len(filtered_appointments)}")
        
        # Get doctor details for each appointment
        result = []
        for apt in filtered_appointments:
            doctor = db.users.find_one({'username': apt['doctor']})
            if doctor:
                # Generate meet link if missing
                if not apt.get('meet_link'):
                    import uuid
                    room_id = f"ckd-appointment-{uuid.uuid4()}"
                    meet_link = f"https://meet.jit.si/{room_id}"
                    apt['meet_link'] = meet_link
                    # Update DB to save this link
                    if '_id' in apt:  # Make sure we have an ID to update
                        db.appointments.update_one(
                            {'_id': apt['_id']},
                            {'$set': {'meet_link': meet_link}}
                        )

                apt['doctor_details'] = {
                    'name': doctor.get('username'),
                    'specialty': doctor.get('specialization', 'Nephrology'),
                    'avatar': doctor.get('username', 'DR')[0:2].upper()
                }
                result.append(apt)
        
        # Sort by date
        result.sort(key=lambda x: (x.get('preferred_date', ''), x.get('preferred_time', '')))
        print(f"Final appointments with doctor details: {len(result)}")
        return result
    except Exception as e:
        print(f"Error getting appointments for patient {patient_username}: {e}")
        import traceback
        traceback.print_exc()
        return []


def save_feedback(feedback_data):
    db = Database.get_db()
    db.feedbacks.insert_one(feedback_data)

def get_all_feedbacks():
    db = Database.get_db()
    return list(db.feedbacks.find())

def get_prescriptions_for_doctor(doctor_username):
    """Fetch prescriptions authored by the given doctor."""
    try:
        db = Database.get_db()
        if db is None:
            return []
        cursor = db.prescriptions.find({'doctor': doctor_username}).sort('date', -1)
        return list(cursor)
    except Exception as e:
        print(f"Error getting prescriptions for doctor {doctor_username}: {e}")
        return []

def create_prescription_record(prescription_data):
    """Persist a new prescription document."""
    try:
        db = Database.get_db()
        if db is None:
            return None
        if not prescription_data.get('date'):
            prescription_data['date'] = pd.Timestamp.now().strftime('%Y-%m-%d')
        prescription_data['created_at'] = pd.Timestamp.now().isoformat()
        result = db.prescriptions.insert_one(prescription_data)
        prescription_data['_id'] = result.inserted_id
        return prescription_data
    except Exception as e:
        print(f"Error creating prescription: {e}")
        return None

def get_prescription_by_id(prescription_id):
    """Fetch a prescription by its ID."""
    try:
        from bson import ObjectId
        db = Database.get_db()
        if db is None:
            return None
        prescription = db.prescriptions.find_one({'_id': ObjectId(prescription_id)})
        return prescription
    except Exception as e:
        print(f"Error getting prescription by ID {prescription_id}: {e}")
        return None

def update_patient_lab_values(username, lab_values, prediction, pdf_path=None, test_type="Lab Report Analysis"):
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
        
    # Add PDF path if provided
    if pdf_path:
        record['latest_lab_pdf'] = pdf_path
            
    # Create history entry
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    history_entry = {
        'date': timestamp,
        'test_type': test_type,
        'metrics': lab_values,
        'prediction': prediction,
        'pdf_path': pdf_path
    }
    
    # Update database
    update_data = {
        '$set': {
            'current_metrics': current_metrics,
            'latest_lab_pdf': pdf_path if pdf_path else record.get('latest_lab_pdf')
        },
        '$push': {'history': history_entry}
    }
    
    # Remove None values from $set to avoid overwriting with None if not provided
    if not pdf_path:
        del update_data['$set']['latest_lab_pdf']
        
    db.patient_records.update_one(
        {'username': username},
        update_data,
        upsert=True
    )

    # Also update patients_data collection to ensure doctor dashboard shows updated values
    try:
        # Prepare patient data update
        patient_data_update = {}
        for k, v in lab_values.items():
            if v is not None:
                patient_data_update[k] = v
        
        # Add prediction data
        if prediction:
            patient_data_update.update({
                'risk_percentage': prediction.get('risk_percentage', 0),
                'stage': prediction.get('stage', 'N/A'),
                'risk_level': prediction.get('risk_level', 'Unknown'),
                'egfr': prediction.get('egfr', None)
            })
        
        # Update patients_data collection
        db.patients_data.update_one(
            {'username': username},
            {'$set': patient_data_update},
            upsert=True  # Create record if it doesn't exist
        )
        print(f"Updated patients_data for {username} with new lab values")
    except Exception as e:
        print(f"Error updating patients_data: {e}")

def update_disease_status(username, disease_type, prediction):
    """
    Update the status for a specific disease type in patient records.
    Stores the latest result for dashboard display.
    """
    try:
        db = Database.get_db()
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        
        status_entry = {
            'last_updated': timestamp,
            'prediction': prediction
        }
        
        # Update specifically the disease_status dictionary
        db.patient_records.update_one(
            {'username': username},
            {'$set': {f'disease_status.{disease_type}': status_entry}},
            upsert=True
        )
        print(f"Updated disease status for {username} - {disease_type}")
    except Exception as e:
        print(f"Error updating disease status: {e}")

    # Sync with lab_results collection for Doctor Dashboard
    try:
        # Prepare lab result document
        lab_result_doc = {
            'patient_username': username,
            'test_date': datetime.datetime.now(),
            'test_type': 'Lab Report Upload',
            'notes': f"Uploaded via Patient Dashboard. Prediction: {prediction if prediction else 'N/A'}",
            'created_at': datetime.datetime.now()
        }
        
        # Map common fields
        if 'egfr' in lab_values:
            lab_result_doc['egfr'] = float(lab_values['egfr'])
        if 'serum_creatinine' in lab_values:
            lab_result_doc['serum_creatinine'] = float(lab_values['serum_creatinine'])
        if 'bp_systolic' in lab_values:
            lab_result_doc['bp_systolic'] = float(lab_values['bp_systolic'])
        if 'bp_diastolic' in lab_values:
            lab_result_doc['bp_diastolic'] = float(lab_values['bp_diastolic'])
            
        # Add other values
        for k, v in lab_values.items():
            if k not in ['egfr', 'serum_creatinine', 'bp_systolic', 'bp_diastolic'] and v is not None:
                lab_result_doc[k] = v
                
        db.lab_results.insert_one(lab_result_doc)
        print(f"Synced lab result for {username} to lab_results collection")
    except Exception as e:
        print(f"Error syncing to lab_results: {e}")

def decrement_trial_count(username):
    """Deprecated:# No changer enforcing trial limits"""
    pass

def get_doctor_patients_with_details(doctor_username):
    """
    Fetch all patients associated with a doctor (via appointments or manual assignment)
    and return their detailed data including 'last_updated'.
    Fetches real-time data from patient_records as primary source.
    """
    try:
        db = Database.get_db()
        
        # Get doctor user to check for manually assigned patients
        doctor = User.get_by_username(doctor_username)
        if not doctor:
            return []

        appointments = get_appointments_for_doctor(doctor_username)
        
        # Filter patients: Only show those who have an appointment with this doctor
        patient_usernames_with_appointments = set(apt['patient'] for apt in appointments)
        
        # Also include patients manually assigned to this doctor (if any)
        if hasattr(doctor, 'patients') and doctor.patients:
            patient_usernames_with_appointments.update(doctor.patients)
            
        filtered_patients = []
        for username in patient_usernames_with_appointments:
            # Fetch patient records (primary source of truth for lab data)
            records = get_patient_records(username)
            
            # Get user info for patient_id
            user = User.get_by_username(username)
            patient_id = f'P{user.id}' if user else f'P{username}'
            
            # Initialize with defaults
            patient_info = {
                'patient_id': patient_id,
                'username': username,
                'name': username,
                'risk_percentage': 0,
                'stage': 'New',
                'risk_level': 'Pending Intake',
                'age': 'N/A',
                'egfr': None,
                'last_updated': 'N/A'
            }
            
            # If patient has records with history, extract real-time data
            if records and 'history' in records and records['history']:
                latest_entry = records['history'][-1]
                
                # Get last updated timestamp
                last_updated = latest_entry.get('date', 'N/A')
                if hasattr(last_updated, 'strftime'):
                    last_updated = last_updated.strftime('%Y-%m-%d %H:%M')
                patient_info['last_updated'] = last_updated
                
                # Get prediction data from latest entry
                prediction = latest_entry.get('prediction', {})
                if prediction and isinstance(prediction, dict):
                    # Extract risk data
                    if 'risk_level' in prediction:
                        patient_info['risk_level'] = str(prediction['risk_level']).title()
                    if 'risk_percentage' in prediction:
                        try:
                            patient_info['risk_percentage'] = float(prediction['risk_percentage'])
                        except (ValueError, TypeError):
                            patient_info['risk_percentage'] = 0
                    if 'stage' in prediction:
                        patient_info['stage'] = prediction['stage']
                    if 'egfr' in prediction:
                        try:
                            patient_info['egfr'] = float(prediction['egfr'])
                        except (ValueError, TypeError):
                            patient_info['egfr'] = None
                
                # Get metrics from latest entry
                metrics = latest_entry.get('metrics', {})
                if metrics and isinstance(metrics, dict):
                    # If prediction didn't have egfr, try metrics
                    if patient_info['egfr'] is None and 'egfr' in metrics:
                        try:
                            patient_info['egfr'] = float(metrics['egfr'])
                        except (ValueError, TypeError):
                            pass
                    
                    # Get age if available
                    if 'age' in metrics:
                        try:
                            patient_info['age'] = int(metrics['age'])
                        except (ValueError, TypeError):
                            pass
                
                # Get current_metrics if available
                current_metrics = records.get('current_metrics', {})
                if current_metrics:
                    # Update with current metrics if they exist
                    if 'age' in current_metrics and patient_info['age'] == 'N/A':
                        try:
                            patient_info['age'] = int(current_metrics['age'])
                        except (ValueError, TypeError):
                            pass

            # Always try to backfill with patients_data if info is missing
            patient_data = db.patients_data.find_one({'username': username})
            if patient_data:
                # Use data from patients_data if available and not already set/valid
                if 'name' in patient_data and (not patient_info['name'] or patient_info['name'] == username):
                    patient_info['name'] = patient_data['name']
                
                if 'risk_level' in patient_data and patient_info['risk_level'] == 'Pending Intake':
                    patient_info['risk_level'] = str(patient_data['risk_level']).title()
                
                if 'risk_percentage' in patient_data and patient_info['risk_percentage'] == 0:
                    try:
                        patient_info['risk_percentage'] = float(patient_data['risk_percentage'])
                    except (ValueError, TypeError):
                        pass
                
                if 'stage' in patient_data and patient_info['stage'] == 'New':
                    patient_info['stage'] = patient_data['stage']
                
                if 'egfr' in patient_data and patient_info['egfr'] is None:
                    try:
                        patient_info['egfr'] = float(patient_data['egfr'])
                    except (ValueError, TypeError):
                        pass
                
                if 'age' in patient_data and patient_info['age'] == 'N/A':
                    try:
                        patient_info['age'] = int(patient_data['age'])
                    except (ValueError, TypeError):
                        pass
            
            filtered_patients.append(patient_info)
        
        return filtered_patients
    except Exception as e:
        print(f"Error in get_doctor_patients_with_details: {e}")
        import traceback
        traceback.print_exc()
        return []

