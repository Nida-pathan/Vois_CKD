import os
import io
import pandas as pd
from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify, send_from_directory
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from models.database import Database
from models.user import (
    User, get_all_doctors, get_all_patients, get_patient_data, save_patient_data, 
    get_all_patients_data, get_patient_records, save_patient_record, get_patient_trials, 
    update_patient_trials, create_appointment, get_appointments_for_doctor, 
    get_appointments_for_patient, save_feedback, get_all_feedbacks
)
from dotenv import load_dotenv
import atexit
import threading

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SESSION_SECRET', 'dev_secret_key')

# Initialize Database
Database.initialize()

# Setup Login Manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.get_by_id(user_id)



@app.route('/test')
def test():
    return "Flask app is working!"

@app.route('/')
def index():
    # Always redirect to landing page
    return redirect(url_for('landing'))

@app.route('/landing')
def landing():
    return render_template('kidneycompanion_landing.html')

@app.route('/auth-choice')
def auth_choice():
    return render_template('auth_choice.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        if not all([username, email, password, confirm_password]):
            flash('All required fields must be filled', 'danger')
            return render_template('register.html')
        
        if password != confirm_password:
            flash('Passwords do not match', 'danger')
            return render_template('register.html')
        
        if User.get_by_username(username):
            flash('Username already exists', 'danger')
            return render_template('register.html')
        
        try:
            # Create new patient user
            User.create_user(username, password, 'patient', email)
            
            # Collect comprehensive medical data
            patient_data = {
                'patient_id': f"P{username}",
                'patient_name': request.form.get('full_name'),
                'username': username,
                'age': int(request.form.get('age', 0)),
                'gender': request.form.get('gender'),
                'blood_type': request.form.get('blood_type', 'N/A'),
                'phone': request.form.get('phone'),
                'email': email,
                'address': request.form.get('address', ''),
                
                # Emergency contact
                'emergency_contact': {
                    'name': request.form.get('emergency_contact_name', ''),
                    'phone': request.form.get('emergency_contact_phone', ''),
                    'relationship': request.form.get('emergency_contact_relationship', '')
                },
                
                # Medical history
                'hypertension': 1 if request.form.get('hypertension') else 0,
                'diabetes_mellitus': 1 if request.form.get('diabetes_mellitus') else 0,
                'coronary_artery_disease': 1 if request.form.get('coronary_artery_disease') else 0,
                'anemia': 1 if request.form.get('anemia') else 0,
                'current_medications': request.form.get('current_medications', ''),
                'allergies': request.form.get('allergies', ''),
                'family_history_kidney': request.form.get('family_history_kidney', 'No'),
                'previous_surgeries': request.form.get('previous_surgeries', ''),
                
                # Lab values (optional)
                'bp_systolic': float(request.form.get('bp_systolic')) if request.form.get('bp_systolic') else None,
                'bp_diastolic': float(request.form.get('bp_diastolic')) if request.form.get('bp_diastolic') else None,
                'serum_creatinine': float(request.form.get('serum_creatinine')) if request.form.get('serum_creatinine') else None,
                'blood_urea': float(request.form.get('blood_urea')) if request.form.get('blood_urea') else None,
                'egfr': float(request.form.get('egfr')) if request.form.get('egfr') else None,
                'hemoglobin': float(request.form.get('hemoglobin')) if request.form.get('hemoglobin') else None,
                'blood_glucose': float(request.form.get('blood_glucose')) if request.form.get('blood_glucose') else None,
                'sodium': float(request.form.get('sodium')) if request.form.get('sodium') else None,
                'potassium': float(request.form.get('potassium')) if request.form.get('potassium') else None,
                'specific_gravity': float(request.form.get('specific_gravity')) if request.form.get('specific_gravity') else None,
                'albumin': float(request.form.get('albumin')) if request.form.get('albumin') else None,
                'sugar': float(request.form.get('sugar')) if request.form.get('sugar') else None,
                
                # Lifestyle
                'smoking': request.form.get('smoking', 'Never'),
                'alcohol': request.form.get('alcohol', 'None'),
                'exercise_frequency': request.form.get('exercise_frequency', 'None'),
                'water_intake': request.form.get('water_intake', '4-6 glasses'),
                'sleep_hours': int(request.form.get('sleep_hours')) if request.form.get('sleep_hours') else None,
                
                # Symptoms
                'symptoms': {
                    'fatigue': 1 if request.form.get('symptom_fatigue') else 0,
                    'pedal_edema': 1 if request.form.get('symptom_swelling') else 0,
                    'urination_changes': 1 if request.form.get('symptom_urination') else 0,
                    'appetite_loss': 1 if request.form.get('symptom_appetite') else 0,
                    'nausea': 1 if request.form.get('symptom_nausea') else 0,
                    'sleep_issues': 1 if request.form.get('symptom_sleep') else 0
                },
                'additional_comments': request.form.get('additional_comments', ''),
                
                # Set pedal_edema and appetite for ML model
                'pedal_edema': 1 if request.form.get('symptom_swelling') else 0,
                'appetite': 0 if request.form.get('symptom_appetite') else 1,  # Inverted: 0 = poor, 1 = good
            }
            
            # Calculate CKD risk if we have necessary lab values
            if patient_data['serum_creatinine'] and patient_data['blood_urea']:
                from models.ckd_model import ckd_model
                
                # Prepare data for ML model (fill missing values with defaults)
                ml_data = {
                    'age': patient_data['age'],
                    'bp_systolic': patient_data['bp_systolic'] or 120,
                    'bp_diastolic': patient_data['bp_diastolic'] or 80,
                    'specific_gravity': patient_data['specific_gravity'] or 1.020,
                    'albumin': patient_data['albumin'] or 0,
                    'sugar': patient_data['sugar'] or 0,
                    'red_blood_cells': 1,  # Default normal
                    'pus_cell': 0,  # Default normal
                    'bacteria': 0,  # Default normal
                    'blood_glucose': patient_data['blood_glucose'] or 100,
                    'blood_urea': patient_data['blood_urea'],
                    'serum_creatinine': patient_data['serum_creatinine'],
                    'sodium': patient_data['sodium'] or 140,
                    'potassium': patient_data['potassium'] or 4.5,
                    'hemoglobin': patient_data['hemoglobin'] or 14,
                    'packed_cell_volume': 44,  # Default
                    'white_blood_cell_count': 8000,  # Default
                    'red_blood_cell_count': 5,  # Default
                    'hypertension': patient_data['hypertension'],
                    'diabetes_mellitus': patient_data['diabetes_mellitus'],
                    'coronary_artery_disease': patient_data['coronary_artery_disease'],
                    'appetite': patient_data['appetite'],
                    'pedal_edema': patient_data['pedal_edema'],
                    'anemia': patient_data['anemia']
                }
                
                # Get prediction
                prediction = ckd_model.predict_risk(ml_data)
                patient_data.update(prediction)
            else:
                # Set default risk assessment
                patient_data['risk_level'] = 'Unknown'
                patient_data['risk_percentage'] = 0
                patient_data['stage'] = 'N/A'
            
            # Save patient medical data to database
            save_patient_record(username, patient_data)
            
            flash('Registration successful! Your medical profile has been created.', 'success')
            
            # Log the user in automatically
            user = User.get_by_username(username)
            login_user(user)
            
            return redirect(url_for('patient_dashboard'))
            
        except Exception as e:
            flash(f'Error during registration: {str(e)}', 'danger')
            return render_template('register.html')
        
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username') or ''
        password = request.form.get('password') or ''
        
        user = User.get_by_username(username)
        
        if user and password and check_password_hash(user.password_hash, password):
            login_user(user)
            flash(f'Welcome, {user.username}!', 'success')
            if user.is_doctor():
                return redirect(url_for('doctor_dashboard'))
            else:
                return redirect(url_for('patient_portal'))
        else:
            flash('Invalid username or password', 'danger')
    
    return render_template('login.html')

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if session.get('admin_logged_in'):
        return redirect(url_for('admin_dashboard'))

    if request.method == 'POST':
        admin_id = request.form.get('admin_id')
        admin_password = request.form.get('admin_password')
        
        # Hardcoded admin credentials (should be moved to env vars in production)
        ADMIN_ID = "admin"
        ADMIN_PASSWORD = "admin123"
        
        if admin_id == ADMIN_ID and admin_password == ADMIN_PASSWORD:
            session['admin_logged_in'] = True
            session['admin_id'] = admin_id
            flash('Admin login successful!', 'success')
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Invalid admin credentials', 'danger')
    
    return render_template('admin_login.html')

@app.route('/admin/dashboard')
def admin_dashboard():
    if not session.get('admin_logged_in'):
        flash('Please login as admin first', 'warning')
        return redirect(url_for('admin_login'))
    
    # Get all doctors
    doctors = get_all_doctors()
    
    # Add patients list to each doctor
    for doctor in doctors:
        doctor.patients = get_all_patients()
    
    # Get feedbacks from database
    feedbacks = get_all_feedbacks()
    
    return render_template('admin_dashboard.html', doctors=doctors, feedbacks=feedbacks)

@app.route('/admin/add_doctor', methods=['POST'])
def add_doctor():
    if not session.get('admin_logged_in'):
        flash('Please login as admin first', 'warning')
        return redirect(url_for('admin_login'))
    
    username = request.form.get('username')
    email = request.form.get('email')
    password = request.form.get('password')
    specialization = request.form.get('specialization')
    
    if not all([username, email, password, specialization]):
        flash('All fields are required', 'danger')
        return redirect(url_for('admin_dashboard'))
    
    # Check if username already exists
    if User.get_by_username(username):
        flash('Username already exists', 'danger')
        return redirect(url_for('admin_dashboard'))
    
    # Create new doctor
    User.create_user(username, password, 'doctor', email, specialization)
    
    flash(f'Doctor {username} added successfully!', 'success')
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/logout')
def admin_logout():
    session.pop('admin_logged_in', None)
    session.pop('admin_id', None)
    flash('Admin logged out successfully', 'info')
    return redirect(url_for('login'))

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged out successfully', 'info')
    return redirect(url_for('index'))

@app.route('/doctor/dashboard')
@login_required
def doctor_dashboard():
    if not current_user.is_doctor():
        flash('Access denied. Doctors only.', 'danger')
        return redirect(url_for('patient_portal'))
    
    all_patients_data = get_all_patients_data()
    appointments = get_appointments_for_doctor(current_user.username)
    
    with open('debug_log.txt', 'a') as f:
        f.write(f"DEBUG: Doctor: {current_user.username}\n")
        f.write(f"DEBUG: Appointments found: {len(appointments)}\n")
        if appointments:
            f.write(f"DEBUG: First appointment: {appointments[0]}\n")
    
    # Filter patients: Only show those who have an appointment with this doctor
    patient_usernames_with_appointments = set(apt['patient'] for apt in appointments)
    
    # Also include patients manually assigned to this doctor (if any)
    if hasattr(current_user, 'patients') and current_user.patients:
        patient_usernames_with_appointments.update(current_user.patients)
    
    with open('debug_log.txt', 'a') as f:
        f.write(f"DEBUG: Patients with appointments: {patient_usernames_with_appointments}\n")
        
    try:
        # Create a lookup for patient data
        patient_data_lookup = {}
        for data in all_patients_data:
            p_username = data.get('username')
            if not p_username and data.get('patient_id', '').startswith('P'):
                 p_username = data.get('patient_id')[1:]
            if p_username:
                patient_data_lookup[p_username] = data
                
        filtered_patients = []
        for username in patient_usernames_with_appointments:
            if username in patient_data_lookup:
                data = patient_data_lookup[username]
                
                # Ensure egfr is a number or None
                egfr = data.get('egfr')
                if isinstance(egfr, str):
                    try:
                        egfr = float(egfr)
                    except ValueError:
                        egfr = None
                        
                filtered_patients.append({
                    'patient_id': data.get('patient_id'),
                    'username': username,  # Add username to the patient data
                    'name': data.get('patient_name', 'Unknown'),
                    'risk_percentage': data.get('risk_percentage', 0),
                    'stage': data.get('stage', 'N/A'),
                    'risk_level': data.get('risk_level', 'Unknown'),
                    'age': data.get('age', 'N/A'),
                    'egfr': egfr
                })
            else:
                # Patient has appointment but no health data yet
                # Fetch basic user info
                user = User.get_by_username(username)
                if user:
                    filtered_patients.append({
                        'patient_id': f"P{user.id}",
                        'username': username,  # Add username to the patient data
                        'name': username, # Fallback to username if real name not available
                        'risk_percentage': 0,
                        'stage': 'New',
                        'risk_level': 'Pending Intake',
                        'age': 'N/A',
                        'egfr': None  # Must be None, not 'N/A', to avoid template formatting error
                    })
    except Exception as e:
        import traceback
        with open('debug_log.txt', 'a') as f:
            f.write(f"Error in doctor_dashboard filtering: {str(e)}\n")
            f.write(traceback.format_exc())
        filtered_patients = [] # Fallback to empty list
    
    return render_template('doctor_dashboard.html', patients=filtered_patients, appointments=appointments)

@app.route('/test_buttons')
@login_required
def test_buttons():
    """Test route to check button functionality"""
    # Get sample patient data for testing
    patients = get_all_patients_data()
    sample_patient = patients[0] if patients else None
    
    return render_template('doctor_dashboard.html', 
                         patients=patients if patients else [],
                         appointments=[],
                         sample_patient=sample_patient)

@app.route('/debug/patient_ids')
@login_required
def debug_patient_ids():
    """Debug route to check patient IDs"""
    patients = get_all_patients_data()
    patient_ids = [p.get('patient_id') for p in patients if p.get('patient_id')]
    
    return jsonify({
        'total_patients': len(patients),
        'patient_ids': patient_ids[:10],  # Show first 10 IDs
        'sample_patient': patients[0] if patients else None
    })

@app.route('/debug/patient_list')
@login_required
def debug_patient_list():
    """Debug route to see what patient data is available"""
    from models.user import get_all_patients_data
    patients = get_all_patients_data()
    
    # Log patient data for debugging
    print("Debug - All patients data:")
    for i, patient in enumerate(patients):
        print(f"  Patient {i}: {patient}")
    
    return jsonify({
        'total_patients': len(patients),
        'patients': patients[:5]  # Show first 5 patients
    })

@app.route('/debug/patient_data')
@login_required
def debug_patient_data():
    """Debug route to check what patient data is available"""
    patients = get_all_patients_data()
    
    # Let's also check what the current user can access
    appointments = []
    allowed_patients = set()
    
    if hasattr(current_user, 'is_doctor') and current_user.is_doctor():
        appointments = get_appointments_for_doctor(current_user.username)
        allowed_patients = set(apt['patient'] for apt in appointments)
        if hasattr(current_user, 'patients') and current_user.patients:
            allowed_patients.update(current_user.patients)
    
    return jsonify({
        'current_user': str(current_user),
        'is_doctor': hasattr(current_user, 'is_doctor') and current_user.is_doctor(),
        'total_patients': len(patients),
        'sample_patients': patients[:3] if patients else [],
        'appointments': appointments,
        'allowed_patients': list(allowed_patients)
    })

@app.route('/api/doctor/dashboard/stats')
@login_required
def get_dashboard_stats():
    """Return dashboard statistics as JSON for AJAX updates"""
    if not current_user.is_doctor():
        return jsonify({'error': 'Access denied'}), 403
    
    all_patients_data = get_all_patients_data()
    
    total_patients = len(all_patients_data)
    high_risk = len([p for p in all_patients_data if p.get('risk_level') in ['High', 'Critical']])
    stage_5 = len([p for p in all_patients_data if p.get('stage') == 5])
    avg_risk = sum([p.get('risk_percentage', 0) for p in all_patients_data]) / total_patients if total_patients > 0 else 0
    
    return jsonify({
        'total_patients': total_patients,
        'high_risk': high_risk,
        'stage_5': stage_5,
        'avg_risk': round(avg_risk, 1)
    })

@app.route('/api/doctor/dashboard/patients')
@login_required
def get_dashboard_patients():
    """Return patient list as JSON for AJAX updates"""
    if not current_user.is_doctor():
        return jsonify({'error': 'Access denied'}), 403
    
    all_patients_data = get_all_patients_data()
    patients = []
    for data in all_patients_data:
        patients.append({
            'patient_id': data.get('patient_id'),
            'name': data.get('patient_name', 'Unknown'),
            'risk_percentage': data.get('risk_percentage', 0),
            'stage': data.get('stage', 'N/A'),
            'risk_level': data.get('risk_level', 'Unknown'),
            'age': data.get('age', 'N/A'),
            'egfr': data.get('egfr')
        })
    
    return jsonify({'patients': patients})


@app.route('/doctor/add-patient', methods=['GET', 'POST'])
@login_required
def add_patient():
    if not current_user.is_doctor():
        flash('Access denied. Doctors only.', 'danger')
        return redirect(url_for('patient_portal'))
    
    if request.method == 'POST':
        patient_data = {
            'patient_id': request.form.get('patient_id'),
            'patient_name': request.form.get('patient_name'),
            'age': int(request.form.get('age', 0)),
            'gender': request.form.get('gender'),
            'bp_systolic': float(request.form.get('bp_systolic', 0)),
            'bp_diastolic': float(request.form.get('bp_diastolic', 0)),
            'specific_gravity': float(request.form.get('specific_gravity', 1.020)),
            'albumin': float(request.form.get('albumin', 0)),
            'sugar': float(request.form.get('sugar', 0)),
            'red_blood_cells': float(request.form.get('red_blood_cells', 1)),
            'pus_cell': float(request.form.get('pus_cell', 0)),
            'bacteria': float(request.form.get('bacteria', 0)),
            'blood_glucose': float(request.form.get('blood_glucose', 100)),
            'blood_urea': float(request.form.get('blood_urea', 20)),
            'serum_creatinine': float(request.form.get('serum_creatinine', 1.0)),
            'sodium': float(request.form.get('sodium', 140)),
            'potassium': float(request.form.get('potassium', 4.5)),
            'hemoglobin': float(request.form.get('hemoglobin', 14)),
            'packed_cell_volume': float(request.form.get('packed_cell_volume', 44)),
            'white_blood_cell_count': float(request.form.get('white_blood_cell_count', 8000)),
            'red_blood_cell_count': float(request.form.get('red_blood_cell_count', 5)),
            'hypertension': int(request.form.get('hypertension', 0)),
            'diabetes_mellitus': int(request.form.get('diabetes_mellitus', 0)),
            'coronary_artery_disease': int(request.form.get('coronary_artery_disease', 0)),
            'appetite': int(request.form.get('appetite', 1)),
            'pedal_edema': int(request.form.get('pedal_edema', 0)),
            'anemia': int(request.form.get('anemia', 0))
        }
        
        from models.ckd_model import ckd_model
        prediction = ckd_model.predict_risk(patient_data)
        
        patient_data.update(prediction)
        save_patient_data(patient_data)
        
        flash(f'Patient {patient_data["patient_name"]} added successfully!', 'success')
        return redirect(url_for('results', patient_id=patient_data['patient_id']))
    
    return render_template('add_patient.html')

@app.route('/doctor/upload-file', methods=['POST'])
@login_required
def upload_file():
    if not current_user.is_doctor():
        return jsonify({'error': 'Access denied'}), 403
    
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    
    file = request.files['file']
    file_type = request.form.get('file_type', 'csv')
    
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if file and file.filename:
        try:
            if file_type == 'csv' and file.filename.endswith('.csv'):
                return process_csv_upload(file)
            elif file_type == 'pdf' and file.filename.endswith('.pdf'):
                return process_pdf_upload(file)
            else:
                return jsonify({'error': 'Invalid file format'}), 400
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    return jsonify({'error': 'Invalid file'}), 400

def process_csv_upload(file):
    df = pd.read_csv(io.StringIO(file.stream.read().decode('utf-8')))
    
    patient_list = df.to_dict('records')
    from models.ckd_model import ckd_model
    results = ckd_model.predict_batch(patient_list)
    
    for result in results:
        patient_id = result.get('patient_id', f"AUTO_{pd.Timestamp.now().timestamp()}")
        result['patient_id'] = patient_id
        save_patient_data(result)
    
    flash(f'Successfully processed {len(results)} patients from CSV', 'success')
    return jsonify({'success': True, 'count': len(results)})

def process_pdf_upload(file):
    import PyPDF2
    
    # For now, we'll just acknowledge the PDF upload
    # In a real implementation, you would extract data from the PDF
    flash('PDF file uploaded successfully. In a full implementation, patient data would be extracted from the PDF.', 'info')
    return jsonify({'success': True, 'message': 'PDF processed successfully'})

@app.route('/results/<patient_id>')
@login_required
def results(patient_id):
    # This route is for patients viewing their own results
    if current_user.is_doctor():
        # Redirect doctors to the doctor-specific route
        return redirect(url_for('doctor_patient_details', patient_id=patient_id))
    
    patient_data = get_patient_data(patient_id)
    
    if not patient_data:
        # Try to find in patient records
        records = get_patient_records(current_user.username)
        if records and records.get('patient_id') == patient_id:
            patient_data = records
    
    if not patient_data:
        flash('Patient not found', 'danger')
        return redirect(url_for('patient_portal'))
    
    return render_template('results.html', patient=patient_data)

@app.route('/doctor/patient/<patient_id>')
@login_required
def doctor_patient_details(patient_id):
    if not current_user.is_doctor():
        flash('Access denied. Doctors only.', 'danger')
        return redirect(url_for('patient_portal'))
    
    print(f"Doctor accessing patient details for ID: {patient_id}")  # Debug log
    
    # Get patient data
    patient_data = get_patient_data(patient_id)
    
    # If not found in patients_data collection, try patient_records
    if not patient_data:
        # Try to find in patient records
        all_patients = get_all_patients_data()
        for patient in all_patients:
            if patient.get('patient_id') == patient_id:
                patient_data = patient
                break
    
    # If still not found, try to get from patient_records collection
    if not patient_data:
        # Try to get patient records by username
        # We need to find the username associated with this patient_id
        all_patients_data = get_all_patients_data()
        patient_username = None
        for patient in all_patients_data:
            if patient.get('patient_id') == patient_id:
                patient_username = patient.get('username')
                break
        
        if patient_username:
            patient_records = get_patient_records(patient_username)
            # Merge with patient data if needed
            patient_info = get_patient_data(patient_id)
            if patient_info:
                if patient_records:
                    patient_records.update(patient_info)
                    patient_data = patient_records
                else:
                    patient_data = patient_info
            elif patient_records:
                patient_data = patient_records
    
    # If we still don't have patient data, create a minimal patient object
    if not patient_data:
        # Create a minimal patient object for display
        patient_data = {
            'patient_id': patient_id,
            'name': 'Unknown Patient',
            'risk_level': 'Unknown',
            'risk_percentage': 0,
            'stage': 'N/A',
            'egfr': 'N/A'
        }
        flash(f'Patient data not found for ID: {patient_id}. Displaying minimal information.', 'warning')
    
    # Get prescriptions for this patient
    from models.database import Database
    db = Database.get_db()
    prescriptions = []
    lab_results = []
    if db is not None:
        # Get prescriptions
        prescriptions_cursor = db.prescriptions.find({'patient': patient_username if patient_username else patient_id})
        prescriptions = list(prescriptions_cursor)
        
        # Get lab results
        lab_results_cursor = db.lab_results.find({'patient_id': patient_id})
        lab_results = list(lab_results_cursor)
    
    # Access Control for Doctors - TEMPORARILY DISABLED FOR DEBUGGING
    # appointments = get_appointments_for_doctor(current_user.username)
    # allowed_patients = set(apt['patient'] for apt in appointments)
    # if hasattr(current_user, 'patients') and current_user.patients:
    #     allowed_patients.update(current_user.patients)
    #     
    # # Check if this patient is in the allowed list
    # p_username = patient_data.get('username') if patient_data else None
    # if not p_username and patient_id.startswith('P'):
    #     p_username = patient_id[1:]
    #     
    # if p_username and p_username not in allowed_patients:
    #     flash('Access denied. You can only view reports for your booked patients.', 'danger')
    #     return redirect(url_for('doctor_dashboard'))

    print(f"Patient data being sent to template: {patient_data}")  # Debug log

    # Additional debugging - let's also print the patient_id to make sure it's correct
    print(f"Final patient_id: {patient_id}")
    print(f"Final patient_data keys: {list(patient_data.keys()) if patient_data else 'None'}")

    return render_template('results.html', 
                         patient=patient_data,
                         prescriptions=prescriptions,
                         lab_results=lab_results)

@app.route('/test/route/debug')
def test_route_debug():
    """Simple test route to verify the server is working"""
    return "Test route is working!"

@app.route('/doctor/patient/test123')
@login_required
def doctor_patient_test():
    """Test route to verify doctor patient route is working"""
    if not current_user.is_doctor():
        return "Not a doctor"
    return "Doctor patient route is working!"

@app.route('/test_direct_access/<patient_id>')
def test_direct_access(patient_id):
    """Test route to verify direct access works"""
    return f"Direct access test successful! Patient ID: {patient_id}"

@app.route('/test_route/<patient_id>')
def test_route(patient_id):
    """Simple test route to verify routing is working"""
    return f"Test route working! Patient ID: {patient_id}"

@app.route('/test_patient_data/<patient_id>')
def test_patient_data(patient_id):
    """Test route to debug patient data retrieval"""
    from models.user import get_patient_data, get_all_patients_data, get_patient_records
    
    # Try different methods to get patient data
    patient_data = get_patient_data(patient_id)
    
    if not patient_data:
        # Try to find in patient records
        all_patients = get_all_patients_data()
        for patient in all_patients:
            if patient.get('patient_id') == patient_id:
                patient_data = patient
                break
    
    # Try to get patient records by username
    if not patient_data:
        all_patients_data = get_all_patients_data()
        patient_username = None
        for patient in all_patients_data:
            if patient.get('patient_id') == patient_id:
                patient_username = patient.get('username')
                break
        
        if patient_username:
            patient_records = get_patient_records(patient_username)
            patient_info = get_patient_data(patient_id)
            if patient_info:
                if patient_records:
                    patient_records.update(patient_info)
                    patient_data = patient_records
                else:
                    patient_data = patient_info
            elif patient_records:
                patient_data = patient_records
    
    return {'patient_id': patient_id, 'patient_data': patient_data}

@app.route('/patient/portal')
@login_required
def patient_portal():
    if current_user.is_doctor():
        return redirect(url_for('doctor_dashboard'))
    
    # Redirect to the new patient dashboard
    return redirect(url_for('patient_dashboard'))

@app.route('/test/patient-dashboard')
def test_patient_dashboard():
    """Test route to check if patient dashboard is accessible"""
    try:
        # Try to render the template with minimal data
        return render_template('patient_dashboard.html', 
                             patient_data={},
                             patient_trials=[],
                             available_doctors=[])
    except Exception as e:
        return f"Error rendering patient dashboard: {str(e)}", 500

@app.route('/test/patient-dashboard-debug')
def test_patient_dashboard_debug():
    """Debug route to check patient dashboard with detailed error info"""
    try:
        # Try to render the template with sample data
        sample_data = {
            'patient_id': 'P123',
            'age': 45,
            'gender': 'Male',
            'blood_type': 'O+',
            'ckd_stage': 'Stage 2',
            'stage_class': 'stage-2',
            'risk_level': 'Moderate',
            'risk_class': 'medium-risk',
            'next_checkup': '2025-12-15',
            'lab_reports_count': 3,
            'current_metrics': {
                'bp_systolic': 130,
                'bp_diastolic': 85,
                'blood_glucose': 95,
                'serum_creatinine': 1.2,
                'egfr': 75,
                'hemoglobin': 14.2,
                'blood_urea': 25,
                'sodium': 140,
                'potassium': 4.2,
                'bp_status': 'warning',
                'glucose_status': 'normal',
                'creatinine_status': 'warning',
                'egfr_status': 'normal'
            },
            'has_history': True,
            'history': [
                {'date': '2025-10-15', 'egfr': 78, 'creatinine': 1.1},
                {'date': '2025-09-15', 'egfr': 80, 'creatinine': 1.0},
                {'date': '2025-08-15', 'egfr': 82, 'creatinine': 0.9}
            ]
        }
        
        return render_template('patient_dashboard.html', 
                             patient_data=sample_data,
                             patient_trials=[{'remaining': 5, 'used': 3}],
                             available_doctors=[{'name': 'Dr. Smith', 'specialty': 'Nephrology'}])
    except Exception as e:
        import traceback
        return f"Error rendering patient dashboard: {str(e)}<br><pre>{traceback.format_exc()}</pre>", 500

@app.route('/patient/dashboard')
@login_required
def patient_dashboard():
    if current_user.is_doctor():
        return redirect(url_for('doctor_dashboard'))
    
    try:
        # Get patient records (Lab History)
        lab_records = get_patient_records(current_user.username)
        
        # Get patient intake data (Personal Info)
        patient_id = f"P{current_user.id}"
        intake_data = get_patient_data(patient_id)
        
        # Merge data: Intake data first, then Lab records override (for metrics/history)
        patient_data = {}
        if intake_data:
            patient_data.update(intake_data)
        if lab_records:
            patient_data.update(lab_records)
        
        # Get patient trial information
        patient_trials = get_patient_trials(current_user.username)
        
        # Get available doctors
        doctors_list = get_all_doctors()
        available_doctors = []
        for doc in doctors_list:
            available_doctors.append({
                'name': f"Dr. {doc.username}",
                'username': doc.username,
                'specialty': doc.specialization or 'General',
                'experience': 'Experienced',
                'avatar': doc.username[:2].upper()
            })
        
        # Prepare dashboard data with defaults
        dashboard_data = {
            'patient_id': patient_data.get('patient_id', 'N/A') if patient_data else 'N/A',
            'age': patient_data.get('age', 'N/A') if patient_data else 'N/A',
            'gender': patient_data.get('gender', 'N/A') if patient_data else 'N/A',
            'blood_type': patient_data.get('blood_type', 'N/A') if patient_data else 'N/A',
            'ckd_stage': 'N/A',
            'stage_class': 'stage-1',
            'risk_level': 'Unknown',
            'risk_class': '',
            'next_checkup': 'Not scheduled',
            'lab_reports_count': 0,
            'current_metrics': {
                'bp_systolic': 'N/A',
                'bp_diastolic': 'N/A',
                'blood_glucose': 'N/A',
                'serum_creatinine': 'N/A',
                'egfr': 'N/A',
                'hemoglobin': 'N/A',
                'blood_urea': 'N/A',
                'sodium': 'N/A',
                'potassium': 'N/A',
                'bp_status': 'unknown',
                'glucose_status': 'unknown',
                'creatinine_status': 'unknown',
                'egfr_status': 'unknown'
            },
            'has_history': False,
            'history': [],
            'latest_lab_pdf': patient_data.get('latest_lab_pdf') if patient_data else None
        }
        
        if patient_data:
            # Calculate CKD stage from eGFR
            egfr = patient_data.get('egfr')
            if egfr:
                if egfr >= 90:
                    dashboard_data['ckd_stage'] = 'Stage 1'
                    dashboard_data['stage_class'] = 'stage-1'
                elif egfr >= 60:
                    dashboard_data['ckd_stage'] = 'Stage 2'
                    dashboard_data['stage_class'] = 'stage-2'
                elif egfr >= 30:
                    dashboard_data['ckd_stage'] = 'Stage 3'
                    dashboard_data['stage_class'] = 'stage-3'
                elif egfr >= 15:
                    dashboard_data['ckd_stage'] = 'Stage 4'
                    dashboard_data['stage_class'] = 'stage-4'
                else:
                    dashboard_data['ckd_stage'] = 'Stage 5'
                    dashboard_data['stage_class'] = 'stage-5'
            
            # Get risk level
            risk_level = patient_data.get('risk_level', 'Unknown')
            dashboard_data['risk_level'] = risk_level
            if risk_level == 'High':
                dashboard_data['risk_class'] = 'high-risk'
            elif risk_level == 'Medium':
                dashboard_data['risk_class'] = 'medium-risk'
            elif risk_level == 'Low':
                dashboard_data['risk_class'] = 'low-risk'
            
            # Get next checkup date
            next_checkup = patient_data.get('next_checkup', 'Not scheduled')
            dashboard_data['next_checkup'] = next_checkup
            
            # Get lab reports count
            lab_reports_count = patient_data.get('lab_reports_count', 0)
            dashboard_data['lab_reports_count'] = lab_reports_count
            
            # Get current metrics
            current_metrics = {
                'bp_systolic': patient_data.get('bp_systolic', 'N/A'),
                'bp_diastolic': patient_data.get('bp_diastolic', 'N/A'),
                'blood_glucose': patient_data.get('blood_glucose', 'N/A'),
                'serum_creatinine': patient_data.get('serum_creatinine', 'N/A'),
                'egfr': patient_data.get('egfr', 'N/A'),
                'hemoglobin': patient_data.get('hemoglobin', 'N/A'),
                'blood_urea': patient_data.get('blood_urea', 'N/A'),
                'sodium': patient_data.get('sodium', 'N/A'),
                'potassium': patient_data.get('potassium', 'N/A'),
                'bp_status': patient_data.get('bp_status', 'unknown'),
                'glucose_status': patient_data.get('glucose_status', 'unknown'),
                'creatinine_status': patient_data.get('creatinine_status', 'unknown'),
                'egfr_status': patient_data.get('egfr_status', 'unknown')
            }
            dashboard_data['current_metrics'] = current_metrics
            
            # Get history
            history = patient_data.get('history', [])
            dashboard_data['history'] = history
            if history:
                dashboard_data['has_history'] = True
        
        return render_template('patient_dashboard.html', 
                             patient_data=dashboard_data,
                             patient_trials=patient_trials,
                             available_doctors=available_doctors)
    
    except Exception as e:
        print(f"Error fetching patient data for dashboard: {e}")
        return render_template('patient_dashboard.html', 
                             patient_data={},
                             patient_trials=[],
                             available_doctors=[])

@app.route('/api/doctor/patient/<patient_id>/health-trends')
@login_required
def get_patient_health_trends(patient_id):
    if not current_user.is_doctor():
        return jsonify({'error': 'Access denied. Doctors only.'}), 403
    
    try:
        # Get patient data
        patient_data = get_patient_data(patient_id)
        
        # Get lab results for this patient
        from models.database import Database
        db = Database.get_db()
        lab_results = []
        if db is not None:
            lab_results_cursor = db.lab_results.find({'patient_id': patient_id})
            lab_results = list(lab_results_cursor)
        
        # Process data for health trends
        egfr_history = []
        bp_history = []
        creatinine_history = []
        
        # Add current patient data point
        if patient_data:
            # eGFR history
            if patient_data.get('egfr') is not None:
                egfr_history.append({
                    'date': 'Current',
                    'value': patient_data['egfr']
                })
            
            # Blood pressure history
            if patient_data.get('bp_systolic') is not None and patient_data.get('bp_diastolic') is not None:
                bp_history.append({
                    'date': 'Current',
                    'systolic': patient_data['bp_systolic'],
                    'diastolic': patient_data['bp_diastolic']
                })
            
            # Serum creatinine history
            if patient_data.get('serum_creatinine') is not None:
                creatinine_history.append({
                    'date': 'Current',
                    'value': patient_data['serum_creatinine']
                })
        
        # Process lab results for historical data
        for result in lab_results:
            # Try to extract relevant data from lab results
            test_type = result.get('test_type', '').lower()
            results = result.get('results', '')
            test_date = result.get('test_date', 'Unknown Date')
            
            # Parse results for numerical values
            try:
                if 'egfr' in test_type or 'glomerular' in test_type:
                    # Extract numerical value from results string
                    import re
                    numbers = re.findall(r'[\d.]+', results)
                    if numbers:
                        egfr_history.append({
                            'date': test_date,
                            'value': float(numbers[0])
                        })
                elif 'blood pressure' in test_type or 'bp' in test_type:
                    # Extract systolic and diastolic values
                    import re
                    numbers = re.findall(r'[\d.]+', results)
                    if len(numbers) >= 2:
                        bp_history.append({
                            'date': test_date,
                            'systolic': float(numbers[0]),
                            'diastolic': float(numbers[1])
                        })
                elif 'creatinine' in test_type:
                    # Extract numerical value from results string
                    import re
                    numbers = re.findall(r'[\d.]+', results)
                    if numbers:
                        creatinine_history.append({
                            'date': test_date,
                            'value': float(numbers[0])
                        })
            except (ValueError, IndexError):
                # Skip malformed data
                continue
        
        # Sort history by date (newest first)
        egfr_history.sort(key=lambda x: x['date'], reverse=True)
        bp_history.sort(key=lambda x: x['date'], reverse=True)
        creatinine_history.sort(key=lambda x: x['date'], reverse=True)
        
        # Limit to last 10 entries for cleaner display
        egfr_history = egfr_history[:10]
        bp_history = bp_history[:10]
        creatinine_history = creatinine_history[:10]
        
        return jsonify({
            'patient_id': patient_id,
            'patient_name': patient_data.get('patient_name', 'Unknown Patient') if patient_data else 'Unknown Patient',
            'egfr_history': egfr_history,
            'bp_history': bp_history,
            'creatinine_history': creatinine_history,
            'lab_results': lab_results
        })
    
    except Exception as e:
        print(f"Error fetching health trends for patient {patient_id}: {e}")
        return jsonify({'error': 'Failed to fetch health trends data'}), 500

@app.route('/api/doctor/patient/<patient_id>/dashboard')
@login_required
def get_patient_dashboard_data(patient_id):
    if not current_user.is_doctor():
        return jsonify({'error': 'Access denied. Doctors only.'}), 403
    
    try:
        # Get patient data
        patient_data = get_patient_data(patient_id)
        
        # Prepare dashboard data with defaults
        dashboard_data = {
            'patient_id': patient_data.get('patient_id', 'N/A') if patient_data else 'N/A',
            'age': patient_data.get('age', 'N/A') if patient_data else 'N/A',
            'gender': patient_data.get('gender', 'N/A') if patient_data else 'N/A',
            'blood_type': patient_data.get('blood_type', 'N/A') if patient_data else 'N/A',
            'ckd_stage': 'N/A',
            'stage_class': 'stage-1',
            'risk_level': 'Unknown',
            'risk_class': '',
            'next_checkup': 'Not scheduled',
            'lab_reports_count': 0,
            'current_metrics': {
                'bp_systolic': 'N/A',
                'bp_diastolic': 'N/A',
                'blood_glucose': 'N/A',
                'serum_creatinine': 'N/A',
                'egfr': 'N/A',
                'hemoglobin': 'N/A',
                'blood_urea': 'N/A',
                'sodium': 'N/A',
                'potassium': 'N/A',
                'bp_status': 'unknown',
                'glucose_status': 'unknown',
                'creatinine_status': 'unknown',
                'egfr_status': 'unknown'
            },
            'has_history': False,
            'history': []
        }
        
        if patient_data:
            # Calculate CKD stage from eGFR
            egfr = patient_data.get('egfr')
            if egfr:
                if egfr >= 90:
                    dashboard_data['ckd_stage'] = 'Stage 1'
                    dashboard_data['stage_class'] = 'stage-1'
                elif egfr >= 60:
                    dashboard_data['ckd_stage'] = 'Stage 2'
                    dashboard_data['stage_class'] = 'stage-2'
                elif egfr >= 30:
                    dashboard_data['ckd_stage'] = 'Stage 3'
                    dashboard_data['stage_class'] = 'stage-3'
                elif egfr >= 15:
                    dashboard_data['ckd_stage'] = 'Stage 4'
                    dashboard_data['stage_class'] = 'stage-4'
                else:
                    dashboard_data['ckd_stage'] = 'Stage 5'
                    dashboard_data['stage_class'] = 'stage-5'
            
            # Get risk level
            risk_level = patient_data.get('risk_level', 'Unknown')
            dashboard_data['risk_level'] = risk_level
            if risk_level == 'High':
                dashboard_data['risk_class'] = 'status-critical'
            elif risk_level == 'Moderate':
                dashboard_data['risk_class'] = 'status-warning'
            elif risk_level == 'Low':
                dashboard_data['risk_class'] = 'status-normal'
            
            # Current metrics
            dashboard_data['current_metrics'] = {
                'bp_systolic': patient_data.get('bp_systolic', 'N/A'),
                'bp_diastolic': patient_data.get('bp_diastolic', 'N/A'),
                'blood_glucose': patient_data.get('blood_glucose', 'N/A'),
                'serum_creatinine': patient_data.get('serum_creatinine', 'N/A'),
                'egfr': patient_data.get('egfr', 'N/A'),
                'hemoglobin': patient_data.get('hemoglobin', 'N/A'),
                'blood_urea': patient_data.get('blood_urea', 'N/A'),
                'sodium': patient_data.get('sodium', 'N/A'),
                'potassium': patient_data.get('potassium', 'N/A')
            }
            
            # Determine status for each metric
            # Blood Pressure
            bp_sys = patient_data.get('bp_systolic')
            bp_dia = patient_data.get('bp_diastolic')
            if bp_sys and bp_dia:
                if bp_sys < 120 and bp_dia < 80:
                    dashboard_data['current_metrics']['bp_status'] = 'normal'
                elif bp_sys < 140 and bp_dia < 90:
                    dashboard_data['current_metrics']['bp_status'] = 'warning'
                else:
                    dashboard_data['current_metrics']['bp_status'] = 'critical'
            
            # Blood Glucose
            glucose = patient_data.get('blood_glucose')
            if glucose:
                if glucose < 100:
                    dashboard_data['current_metrics']['glucose_status'] = 'normal'
                elif glucose < 126:
                    dashboard_data['current_metrics']['glucose_status'] = 'warning'
                else:
                    dashboard_data['current_metrics']['glucose_status'] = 'critical'
            
            # Creatinine
            creatinine = patient_data.get('serum_creatinine')
            if creatinine:
                if creatinine <= 1.2:
                    dashboard_data['current_metrics']['creatinine_status'] = 'normal'
                elif creatinine <= 2.0:
                    dashboard_data['current_metrics']['creatinine_status'] = 'warning'
                else:
                    dashboard_data['current_metrics']['creatinine_status'] = 'critical'
            
            # eGFR
            if egfr:
                if egfr >= 60:
                    dashboard_data['current_metrics']['egfr_status'] = 'normal'
                elif egfr >= 30:
                    dashboard_data['current_metrics']['egfr_status'] = 'warning'
                else:
                    dashboard_data['current_metrics']['egfr_status'] = 'critical'
            
            # History data for charts
            if 'history' in patient_data and patient_data['history']:
                dashboard_data['has_history'] = True
                dashboard_data['history'] = patient_data['history']
                dashboard_data['lab_reports_count'] = len(patient_data['history'])
        
        # Generate personalized lifestyle recommendations
        lifestyle_recommendations = []
        
        if patient_data:
            # Hydration recommendation based on water intake
            water_intake = patient_data.get('water_intake', '4-6 glasses')
            if '<4 glasses' in water_intake:
                lifestyle_recommendations.append({
                    'icon': 'fa-tint',
                    'title': 'Hydration',
                    'description': 'You\'re drinking less than 4 glasses daily. Increase to 8-10 glasses of water daily. Limit fluid intake if advised by doctor.'
                })
            elif '4-6 glasses' in water_intake:
                lifestyle_recommendations.append({
                    'icon': 'fa-tint',
                    'title': 'Hydration',
                    'description': 'Good progress! Aim for 8-10 glasses of water daily. Limit fluid intake if advised by doctor.'
                })
            else:
                lifestyle_recommendations.append({
                    'icon': 'fa-tint',
                    'title': 'Hydration',
                    'description': 'Excellent! You\'re drinking ' + water_intake + ' daily. Maintain this level. Limit fluid intake if advised by doctor.'
                })
            
            # Low Sodium Diet (always recommended for CKD)
            lifestyle_recommendations.append({
                'icon': 'fa-carrot',
                'title': 'Low Sodium Diet',
                'description': 'Limit sodium intake to less than 2,300mg per day. Avoid processed foods.'
            })
            
            # Exercise recommendation based on exercise frequency
            exercise_freq = patient_data.get('exercise_frequency', 'None')
            if exercise_freq == 'None':
                lifestyle_recommendations.append({
                    'icon': 'fa-dumbbell',
                    'title': 'Regular Exercise',
                    'description': 'Start with 15-20 minutes of light exercise, 3 days a week. Walking, swimming recommended. Gradually increase to 30 minutes, 5 days a week.'
                })
            elif '1-2 times/week' in exercise_freq:
                lifestyle_recommendations.append({
                    'icon': 'fa-dumbbell',
                    'title': 'Regular Exercise',
                    'description': 'Good start! Increase to 30 minutes of moderate exercise, 5 days a week. Walking, swimming recommended.'
                })
            elif '3-4 times/week' in exercise_freq:
                lifestyle_recommendations.append({
                    'icon': 'fa-dumbbell',
                    'title': 'Regular Exercise',
                    'description': 'Great job! Aim for 30 minutes of moderate exercise, 5 days a week. Walking, swimming recommended.'
                })
            else:
                lifestyle_recommendations.append({
                    'icon': 'fa-dumbbell',
                    'title': 'Regular Exercise',
                    'description': 'Excellent! You\'re exercising 5+ times per week. Maintain 30 minutes of moderate exercise. Walking, swimming recommended.'
                })
            
            # Sleep recommendation based on sleep hours
            sleep_hours = patient_data.get('sleep_hours')
            if sleep_hours:
                if sleep_hours < 6:
                    lifestyle_recommendations.append({
                        'icon': 'fa-bed',
                        'title': 'Sleep Schedule',
                        'description': f'You\'re getting only {sleep_hours} hours of sleep. Aim for 7-8 hours of quality sleep. Fixed bedtime routine recommended.'
                    })
                elif sleep_hours >= 6 and sleep_hours < 7:
                    lifestyle_recommendations.append({
                        'icon': 'fa-bed',
                        'title': 'Sleep Schedule',
                        'description': f'Good! You\'re getting {sleep_hours} hours. Aim for 7-8 hours of quality sleep. Fixed bedtime routine recommended.'
                    })
                elif sleep_hours >= 7 and sleep_hours <= 8:
                    lifestyle_recommendations.append({
                        'icon': 'fa-bed',
                        'title': 'Sleep Schedule',
                        'description': f'Perfect! You\'re getting {sleep_hours} hours of quality sleep. Maintain this schedule. Fixed bedtime routine recommended.'
                    })
                else:
                    lifestyle_recommendations.append({
                        'icon': 'fa-bed',
                        'title': 'Sleep Schedule',
                        'description': f'You\'re sleeping {sleep_hours} hours. Aim for 7-8 hours of quality sleep. Fixed bedtime routine recommended.'
                    })
            else:
                lifestyle_recommendations.append({
                    'icon': 'fa-bed',
                    'title': 'Sleep Schedule',
                    'description': 'Maintain 7-8 hours of quality sleep. Fixed bedtime routine recommended.'
                })
            
            # Smoking cessation if applicable
            smoking_status = patient_data.get('smoking', 'Never')
            if smoking_status == 'Current':
                lifestyle_recommendations.insert(1, {
                    'icon': 'fa-smoking-ban',
                    'title': 'Quit Smoking',
                    'description': 'Smoking significantly worsens kidney disease. Seek support to quit smoking immediately. Talk to your doctor about cessation programs.'
                })
            elif smoking_status == 'Former':
                lifestyle_recommendations.insert(1, {
                    'icon': 'fa-check-circle',
                    'title': 'Smoke-Free',
                    'description': 'Congratulations on quitting smoking! Stay smoke-free to protect your kidney health.'
                })
        else:
            # Default recommendations if no patient data
            lifestyle_recommendations = [
                {
                    'icon': 'fa-tint',
                    'title': 'Hydration',
                    'description': 'Drink 8-10 glasses of water daily. Limit fluid intake if advised by doctor.'
                },
                {
                    'icon': 'fa-carrot',
                    'title': 'Low Sodium Diet',
                    'description': 'Limit sodium intake to less than 2,300mg per day. Avoid processed foods.'
                },
                {
                    'icon': 'fa-dumbbell',
                    'title': 'Regular Exercise',
                    'description': '30 minutes of moderate exercise, 5 days a week. Walking, swimming recommended.'
                },
                {
                    'icon': 'fa-bed',
                    'title': 'Sleep Schedule',
                    'description': 'Maintain 7-8 hours of quality sleep. Fixed bedtime routine recommended.'
                }
            ]
        
        dashboard_data['lifestyle_recommendations'] = lifestyle_recommendations
        
        return render_template('patient_dashboard.html', 
                             patient=patient_data, 
                             trials=patient_trials,
                             doctors=available_doctors,
                             dashboard=dashboard_data)
    
    except Exception as e:
        print(f"Error in patient_dashboard: {e}")
        # Return a simplified dashboard in case of errors
        return render_template('patient_dashboard.html', 
                             patient=None, 
                             trials={'remaining': 2, 'used': 0},
                             doctors=[],
                             dashboard={
                                 'patient_id': 'N/A',
                                 'age': 'N/A',
                                 'gender': 'N/A',
                                 'blood_type': 'N/A',
                                 'ckd_stage': 'N/A',
                                 'stage_class': 'stage-1',
                                 'risk_level': 'Unknown',
                                 'risk_class': '',
                                 'next_checkup': 'Not scheduled',
                                 'lab_reports_count': 0,
                                 'current_metrics': {
                                     'bp_systolic': 'N/A',
                                     'bp_diastolic': 'N/A',
                                     'blood_glucose': 'N/A',
                                     'serum_creatinine': 'N/A',
                                     'egfr': 'N/A',
                                     'hemoglobin': 'N/A',
                                     'blood_urea': 'N/A',
                                     'sodium': 'N/A',
                                     'potassium': 'N/A',
                                     'bp_status': 'unknown',
                                     'glucose_status': 'unknown',
                                     'creatinine_status': 'unknown',
                                     'egfr_status': 'unknown'
                                 },
                                 'has_history': False,
                                 'history': [],
                                 'lifestyle_recommendations': [
                                     {
                                         'icon': 'fa-tint',
                                         'title': 'Hydration',
                                         'description': 'Drink 8-10 glasses of water daily. Limit fluid intake if advised by doctor.'
                                     },
                                     {
                                         'icon': 'fa-carrot',
                                         'title': 'Low Sodium Diet',
                                         'description': 'Limit sodium intake to less than 2,300mg per day. Avoid processed foods.'
                                     },
                                     {
                                         'icon': 'fa-dumbbell',
                                         'title': 'Regular Exercise',
                                         'description': '30 minutes of moderate exercise, 5 days a week. Walking, swimming recommended.'
                                     },
                                     {
                                         'icon': 'fa-bed',
                                         'title': 'Sleep Schedule',
                                         'description': 'Maintain 7-8 hours of quality sleep. Fixed bedtime routine recommended.'
                                     }
                                 ]
                             })



@app.route('/patient/book-appointment', methods=['POST'])
@login_required
def book_appointment():
    if current_user.is_doctor():
        return jsonify({'error': 'Access denied'}), 403
    
    data = request.get_json()
    doctor_name = data.get('doctor_name')
    preferred_date = data.get('preferred_date')
    preferred_time = data.get('preferred_time')
    
    try:
        with open('debug_log.txt', 'a') as f:
            f.write(f"Booking request received: {data}\n")
            f.write(f"Doctor name: {doctor_name}\n")
            
        if not doctor_name:
            return jsonify({'error': 'Doctor name is required'}), 400
        
        # Create appointment record (simplified)
        appointment = {
            'patient': current_user.username,
            'doctor': doctor_name,
            'preferred_date': preferred_date,
            'preferred_time': preferred_time,
            'status': 'pending',
            'created_at': pd.Timestamp.now().isoformat()
        }
        
        # Save to database
        create_appointment(appointment)
        
        # Convert ObjectId to string for JSON serialization
        if '_id' in appointment:
            appointment['_id'] = str(appointment['_id'])
        
        with open('debug_log.txt', 'a') as f:
            f.write(f"Appointment created successfully: {appointment}\n")
        
        return jsonify({
            'status': 'success', 
            'message': f'Appointment request sent to {doctor_name}. You will be notified shortly.',
            'appointment': appointment
        })
    except Exception as e:
        with open('debug_log.txt', 'a') as f:
            f.write(f"Error in book_appointment: {str(e)}\n")
        return jsonify({'error': str(e)}), 500


# Phase 2: Communication & Scheduling Routes

@app.route('/appointments')
@login_required
def appointments():
    if not current_user.is_doctor():
        return redirect(url_for('index'))
    
    from models.user import get_appointments_for_doctor
    appointments_list = get_appointments_for_doctor(current_user.username)
    return render_template('appointments.html', appointments=appointments_list)

@app.route('/create_appointment', methods=['POST'])
@login_required
def create_appointment_route():
    if not current_user.is_doctor():
        return redirect(url_for('index'))
        
    appointment_data = {
        'doctor': current_user.username,
        'patient_name': request.form.get('patient_name'),
        'date': request.form.get('date'),
        'time': request.form.get('time'),
        'type': request.form.get('type'),
        'notes': request.form.get('notes'),
        'created_at': pd.Timestamp.now().isoformat()
    }
    
    from models.user import create_appointment
    create_appointment(appointment_data)
    flash('Appointment scheduled successfully', 'success')
    return redirect(url_for('appointments'))

@app.route('/messages')
@login_required
def messages():
    from models.user import Message, get_all_patients
    contacts = Message.get_conversations(current_user.username)
    # Add all patients as contacts for doctors
    if current_user.is_doctor():
        patients = get_all_patients()
        for p in patients:
            if p.username not in contacts:
                contacts.append(p.username)
    
    return render_template('messages.html', contacts=contacts)

@app.route('/get_messages/<username>')
@login_required
def get_messages(username):
    from models.user import Message
    messages_list = Message.get_messages(current_user.username, username)
    return jsonify([{
        'sender': msg.sender,
        'recipient': msg.recipient,
        'content': msg.content,
        'timestamp': msg.timestamp
    } for msg in messages_list])

@app.route('/send_message', methods=['POST'])
@login_required
def send_message():
    from models.user import Message
    recipient = request.form.get('recipient')
    content = request.form.get('content')
    
    if not recipient or not content:
        return jsonify({'success': False, 'error': 'Missing data'}), 400
    
    Message.send_message(current_user.username, recipient, content)
    return jsonify({'success': True})

# Phase 3: Clinical Tools Routes

@app.route('/prescriptions')
@login_required
def prescriptions():
    if not current_user.is_doctor():
        return redirect(url_for('index'))
    
    from models.user import Prescription
    prescriptions_list = Prescription.get_by_doctor(current_user.username)
    return render_template('prescriptions.html', prescriptions=prescriptions_list)

@app.route('/create_prescription', methods=['POST'])
@login_required
def create_prescription():
    if not current_user.is_doctor():
        return redirect(url_for('index'))
    
    # Parse medications from form
    med_names = request.form.getlist('med_name[]')
    med_dosages = request.form.getlist('med_dosage[]')
    med_frequencies = request.form.getlist('med_frequency[]')
    
    medications = []
    for name, dosage, frequency in zip(med_names, med_dosages, med_frequencies):
        medications.append({
            'name': name,
            'dosage': dosage,
            'frequency': frequency
        })
    
    prescription_data = {
        'doctor': current_user.username,
        'patient': request.form.get('patient'),
        'date': request.form.get('date'),
        'medications': medications,
        'notes': request.form.get('notes', '')
    }
    
    from models.user import Prescription
    Prescription.create(prescription_data)
    flash('Prescription created successfully', 'success')
    return redirect(url_for('prescriptions'))

@app.route('/lab_results')
@login_required
def lab_results():
    if not current_user.is_doctor():
        return redirect(url_for('index'))
    
    # For now, return empty list - can be extended later
    return render_template('lab_results.html', results=[])

@app.route('/education')
@login_required
def education():
    return render_template('education.html')

@app.route('/patient/therapy-plan')
@login_required
def therapy_plan():
    """Display the therapy recommendations plan"""
    if current_user.is_doctor():
        return redirect(url_for('doctor_dashboard'))
    
    return render_template('therapy_plan.html')

@app.route('/patient/diet-plan')
@login_required
def diet_plan():
    """Display detailed diet and lifestyle plan"""
    if current_user.is_doctor():
        return redirect(url_for('doctor_dashboard'))
    
    # Get patient records
    patient_data = get_patient_records(current_user.username)
    
    # Generate personalized lifestyle recommendations (same logic as dashboard)
    lifestyle_recommendations = []
    
    if patient_data:
        # Hydration recommendation
        water_intake = patient_data.get('water_intake', '4-6 glasses')
        if '<4 glasses' in water_intake:
            lifestyle_recommendations.append({
                'icon': 'fa-tint',
                'title': 'Hydration',
                'description': 'You\'re drinking less than 4 glasses daily. Increase to 8-10 glasses of water daily. Limit fluid intake if advised by doctor.',
                'status': 'needs-improvement',
                'status_text': 'Needs Improvement'
            })
        elif '4-6 glasses' in water_intake:
            lifestyle_recommendations.append({
                'icon': 'fa-tint',
                'title': 'Hydration',
                'description': 'Good progress! Aim for 8-10 glasses of water daily. Limit fluid intake if advised by doctor.',
                'status': 'good',
                'status_text': 'Good Progress'
            })
        else:
            lifestyle_recommendations.append({
                'icon': 'fa-tint',
                'title': 'Hydration',
                'description': 'Excellent! You\'re drinking ' + water_intake + ' daily. Maintain this level. Limit fluid intake if advised by doctor.',
                'status': 'excellent',
                'status_text': 'Excellent'
            })
        
        # Low Sodium Diet
        lifestyle_recommendations.append({
            'icon': 'fa-carrot',
            'title': 'Low Sodium Diet',
            'description': 'Limit sodium intake to less than 2,300mg per day. Avoid processed foods.',
            'status': None,
            'status_text': None
        })
        
        # Exercise recommendation
        exercise_freq = patient_data.get('exercise_frequency', 'None')
        if exercise_freq == 'None':
            lifestyle_recommendations.append({
                'icon': 'fa-dumbbell',
                'title': 'Regular Exercise',
                'description': 'Start with 15-20 minutes of light exercise, 3 days a week. Walking, swimming recommended. Gradually increase to 30 minutes, 5 days a week.',
                'status': 'needs-improvement',
                'status_text': 'Get Started'
            })
        elif '1-2 times/week' in exercise_freq:
            lifestyle_recommendations.append({
                'icon': 'fa-dumbbell',
                'title': 'Regular Exercise',
                'description': 'Good start! Increase to 30 minutes of moderate exercise, 5 days a week. Walking, swimming recommended.',
                'status': 'good',
                'status_text': 'Good Start'
            })
        elif '3-4 times/week' in exercise_freq:
            lifestyle_recommendations.append({
                'icon': 'fa-dumbbell',
                'title': 'Regular Exercise',
                'description': 'Great job! Aim for 30 minutes of moderate exercise, 5 days a week. Walking, swimming recommended.',
                'status': 'good',
                'status_text': 'Great Progress'
            })
        else:
            lifestyle_recommendations.append({
                'icon': 'fa-dumbbell',
                'title': 'Regular Exercise',
                'description': 'Excellent! You\'re exercising 5+ times per week. Maintain 30 minutes of moderate exercise. Walking, swimming recommended.',
                'status': 'excellent',
                'status_text': 'Excellent'
            })
        
        # Sleep recommendation
        sleep_hours = patient_data.get('sleep_hours')
        if sleep_hours:
            if sleep_hours < 6:
                lifestyle_recommendations.append({
                    'icon': 'fa-bed',
                    'title': 'Sleep Schedule',
                    'description': f'You\'re getting only {sleep_hours} hours of sleep. Aim for 7-8 hours of quality sleep. Fixed bedtime routine recommended.',
                    'status': 'critical',
                    'status_text': 'Critical - Too Little'
                })
            elif sleep_hours >= 6 and sleep_hours < 7:
                lifestyle_recommendations.append({
                    'icon': 'fa-bed',
                    'title': 'Sleep Schedule',
                    'description': f'Good! You\'re getting {sleep_hours} hours. Aim for 7-8 hours of quality sleep. Fixed bedtime routine recommended.',
                    'status': 'good',
                    'status_text': 'Almost There'
                })
            elif sleep_hours >= 7 and sleep_hours <= 8:
                lifestyle_recommendations.append({
                    'icon': 'fa-bed',
                    'title': 'Sleep Schedule',
                    'description': f'Perfect! You\'re getting {sleep_hours} hours of quality sleep. Maintain this schedule. Fixed bedtime routine recommended.',
                    'status': 'excellent',
                    'status_text': 'Perfect'
                })
            else:
                lifestyle_recommendations.append({
                    'icon': 'fa-bed',
                    'title': 'Sleep Schedule',
                    'description': f'You\'re sleeping {sleep_hours} hours. Aim for 7-8 hours of quality sleep. Fixed bedtime routine recommended.',
                    'status': 'needs-improvement',
                    'status_text': 'Too Much'
                })
        else:
            lifestyle_recommendations.append({
                'icon': 'fa-bed',
                'title': 'Sleep Schedule',
                'description': 'Maintain 7-8 hours of quality sleep. Fixed bedtime routine recommended.',
                'status': None,
                'status_text': None
            })
        
        # Smoking cessation
        smoking_status = patient_data.get('smoking', 'Never')
        if smoking_status == 'Current':
            lifestyle_recommendations.insert(1, {
                'icon': 'fa-smoking-ban',
                'title': 'Quit Smoking',
                'description': 'Smoking significantly worsens kidney disease. Seek support to quit smoking immediately. Talk to your doctor about cessation programs.',
                'status': 'critical',
                'status_text': 'Critical Action Needed'
            })
        elif smoking_status == 'Former':
            lifestyle_recommendations.insert(1, {
                'icon': 'fa-check-circle',
                'title': 'Smoke-Free',
                'description': 'Congratulations on quitting smoking! Stay smoke-free to protect your kidney health.',
                'status': 'excellent',
                'status_text': 'Excellent Achievement'
            })
    else:
        # Default recommendations
        lifestyle_recommendations = [
            {
                'icon': 'fa-tint',
                'title': 'Hydration',
                'description': 'Drink 8-10 glasses of water daily. Limit fluid intake if advised by doctor.',
                'status': None,
                'status_text': None
            },
            {
                'icon': 'fa-carrot',
                'title': 'Low Sodium Diet',
                'description': 'Limit sodium intake to less than 2,300mg per day. Avoid processed foods.',
                'status': None,
                'status_text': None
            },
            {
                'icon': 'fa-dumbbell',
                'title': 'Regular Exercise',
                'description': '30 minutes of moderate exercise, 5 days a week. Walking, swimming recommended.',
                'status': None,
                'status_text': None
            },
            {
                'icon': 'fa-bed',
                'title': 'Sleep Schedule',
                'description': 'Maintain 7-8 hours of quality sleep. Fixed bedtime routine recommended.',
                'status': None,
                'status_text': None
            }
        ]
    
    return render_template('diet_plan.html', lifestyle_recommendations=lifestyle_recommendations)

@app.route('/patient/ai-lifestyle-plan')
@login_required
def ai_lifestyle_plan():
    """AI-powered personalized lifestyle plan page"""
    if current_user.is_doctor():
        return redirect(url_for('doctor_dashboard'))
    
    # Get patient data
    patient_data = get_patient_records(current_user.username)
    
    # Check for existing AI recommendations
    from models.database import get_ai_recommendations
    recommendations = get_ai_recommendations(current_user.username)
    
    return render_template('ai_lifestyle_plan.html',
                         patient=patient_data,
                         recommendations=recommendations)

@app.route('/patient/generate-ai-recommendations', methods=['POST'])
@login_required
def generate_ai_recommendations():
    """API endpoint to generate AI recommendations"""
    if current_user.is_doctor():
        return jsonify({'success': False, 'error': 'Access denied'}), 403
    
    try:
        # Get patient data
        patient_data = get_patient_records(current_user.username)
        
        if not patient_data:
            return jsonify({
                'success': False,
                'error': 'Patient data not found'
            }), 404
        
        # Initialize AI recommender
        from models.ai_recommender import CKDAIRecommender
        recommender = CKDAIRecommender()
        
        # Generate comprehensive plan
        recommendations = recommender.generate_comprehensive_plan(patient_data)
        
        # Save to database
        from models.database import save_ai_recommendations
        save_ai_recommendations(current_user.username, recommendations)
        
        return jsonify({
            'success': True,
            'recommendations': recommendations
        })
    
    except ValueError as e:
        # API key not configured
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
    except Exception as e:
        print(f"Error generating AI recommendations: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to generate recommendations. Please try again later.'
        }), 500



@app.route('/patient/lab-analysis')
@login_required
def lab_analysis():
    """Render the lab analysis page with disease selection"""
    if current_user.is_doctor():
        return redirect(url_for('doctor_dashboard'))
    return render_template('lab_analysis.html')

@app.route('/patient/upload-lab', methods=['POST'])
@login_required
def upload_lab_report_pdf():
    """Upload and analyze lab report PDF"""
    if current_user.is_doctor():
        return jsonify({'error': 'Access denied'}), 403
    
    # Check if file was uploaded
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    
    file = request.files['file']
    disease_type = request.form.get('disease_type', 'ckd')
    use_defaults = request.form.get('use_defaults', 'false') == 'true'
    
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    # Check file extension
    if not file.filename.lower().endswith('.pdf'):
        return jsonify({'error': 'Only PDF files are allowed'}), 400
    
    try:
        from models.pdf_parser import LabReportParser
        from models.disease_predictor import KidneyDiseasePredictor
        from werkzeug.utils import secure_filename
        import os
        
        # Create uploads directory if it doesn't exist
        upload_folder = 'static/uploads/lab_reports'
        os.makedirs(upload_folder, exist_ok=True)
        
        # Save uploaded file
        filename = secure_filename(f"{current_user.username}_{disease_type}_{file.filename}")
        filepath = os.path.join(upload_folder, filename)
        file.save(filepath)
        
        # Parse PDF and extract values
        parser = LabReportParser(filepath)
        
        if use_defaults:
            # Use default values for testing
            lab_values = parser.set_default_values(disease_type)
        else:
            # Extract from PDF
            lab_values = parser.extract_values(disease_type)
        
        if not lab_values:
            # If no values extracted, use defaults
            lab_values = parser.set_default_values(disease_type)
        
        # Predict disease severity
        predictor = KidneyDiseasePredictor()
        
        if disease_type == 'ckd':
            prediction = predictor.predict_ckd(lab_values)
        elif disease_type == 'kidney_stone':
            prediction = predictor.predict_kidney_stone(lab_values)
        elif disease_type == 'aki':
            prediction = predictor.predict_aki(lab_values)
        elif disease_type == 'esrd':
            prediction = predictor.predict_esrd(lab_values)
        else:
            return jsonify({'error': 'Invalid disease type'}), 400
        
        # Update patient records with extracted values
        from models.user import update_patient_lab_values
        # Store relative path for frontend access
        relative_path = f"uploads/lab_reports/{filename}"
        update_patient_lab_values(current_user.username, lab_values, prediction, relative_path)
        
        # Trial count logic removed as per request
        
        return jsonify({
            'success': True,
            'message': f'{prediction["disease"]} analysis complete!',
            'extracted_values': lab_values,
            'prediction': prediction
        })
    
    except Exception as e:
        print(f"Error processing lab report: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Failed to process lab report: {str(e)}'}), 500



@app.route('/kidneycompanion')
def kidneycompanion_landing():
    return render_template('kidneycompanion_landing.html')

@app.route('/disease/<disease_id>')
def disease_detail(disease_id):
    # Map disease IDs to human-readable names and detailed information
    disease_info = {
        'ckd': {
            'name': 'Chronic Kidney Disease',
            'description': 'Chronic Kidney Disease (CKD) is a long-term condition where the kidneys don\'t work as well as they should. It\'s a common condition often associated with aging, affecting around 1 in 10 people.',
            'stages': 'CKD is classified into 5 stages based on the glomerular filtration rate (GFR):\n'
                      '- Stage 1: Normal or high GFR (>90 mL/min)\n'
                      '- Stage 2: Mild CKD (60-89 mL/min)\n'
                      '- Stage 3: Moderate CKD (30-59 mL/min)\n'
                      '- Stage 4: Severe CKD (15-29 mL/min)\n'
                      '- Stage 5: End Stage CKD (<15 mL/min)',
            'symptoms': 'Early stages may have no symptoms. As CKD progresses, symptoms may include:\n'
                        '- Tiredness\n'
                        '- Swollen ankles, feet or hands\n'
                        '- Shortness of breath\n'
                        '- Nausea\n'
                        '- Blood in urine\n'
                        '- High blood pressure',
            'causes': 'Common causes include:\n'
                      '- Diabetes (diabetic nephropathy)\n'
                      '- High blood pressure (hypertensive nephropathy)\n'
                      '- Glomerulonephritis\n'
                      '- Polycystic kidney disease\n'
                      '- Blocked urinary tract\n'
                      '- Repeated urinary infections',
            'prevention': 'To reduce your risk:\n'
                         '- Keep blood pressure and blood sugar under control\n'
                         '- Maintain a healthy weight\n'
                         '- Eat a balanced diet\n'
                         '- Exercise regularly\n'
                         '- Don\'t smoke\n'
                         '- Limit alcohol intake\n'
                         '- Take medications as prescribed'
        },
        'diabetic-nephropathy': {
            'name': 'Diabetic Nephropathy',
            'description': 'Diabetic nephropathy is kidney disease that occurs as a result of diabetes. It\'s a leading cause of end-stage kidney disease and affects approximately 20-40% of patients with diabetes.',
            'stages': 'The progression typically follows these stages:\n'
                      '1. Hyperfiltration - Increased kidney function\n'
                      '2. Microalbuminuria - Small amounts of protein in urine\n'
                      '3. Proteinuria - Large amounts of protein in urine\n'
                      '4. Declining kidney function - Reduced GFR\n'
                      '5. End-stage renal disease - Kidney failure',
            'symptoms': 'Early stages may be asymptomatic. Later symptoms include:\n'
                        '- Protein in urine (foamy urine)\n'
                        '- Swelling in legs, ankles, and feet\n'
                        '- Increased urination\n'
                        '- Fatigue\n'
                        '- Loss of appetite\n'
                        '- Nausea and vomiting\n'
                        '- Persistent itching',
            'causes': 'Primary cause is uncontrolled diabetes leading to:\n'
                      '- Damage to blood vessels in kidneys\n'
                      '- Scarring of kidney filtering units (glomeruli)\n'
                      '- Reduced kidney function over time',
            'prevention': 'Key prevention strategies:\n'
                         '- Maintain tight blood sugar control\n'
                         '- Manage blood pressure (target <130/80 mmHg)\n'
                         '- Follow a diabetic diet\n'
                         '- Regular exercise\n'
                         '- Take prescribed medications (ACE inhibitors or ARBs)\n'
                         '- Regular monitoring of kidney function\n'
                         '- Avoid nephrotoxic substances'
        },
        'aki': {
            'name': 'Acute Kidney Injury',
            'description': 'Acute Kidney Injury (AKI) is a sudden episode of kidney failure or kidney damage that happens within a few hours or a few days. It causes a build-up of waste products in your blood and makes it hard for your kidneys to keep the right balance of fluid in your body.',
            'stages': 'AKI is classified by KDIGO criteria:\n'
                      'Stage 1: Increase in serum creatinine by 1.5-1.9 times baseline or GFR decrease >25%\n'
                      'Stage 2: Increase in serum creatinine by 2.0-2.9 times baseline\n'
                      'Stage 3: Increase in serum creatinine by 3.0 times baseline or initiation of renal replacement therapy',
            'symptoms': 'Symptoms may include:\n'
                        '- Decreased urine output\n'
                        '- Fluid retention causing swelling in legs, ankles or feet\n'
                        '- Shortness of breath\n'
                        '- Fatigue\n'
                        '- Confusion\n'
                        '- Nausea\n'
                        '- Seizures or coma in severe cases',
            'causes': 'Three main categories:\n'
                      '1. Prerenal - Decreased blood flow to kidneys:\n'
                      '   - Dehydration\n'
                      '   - Blood loss\n'
                      '   - Heart failure\n'
                      '2. Intrinsic - Direct damage to kidney tissue:\n'
                      '   - Acute tubular necrosis\n'
                      '   - Glomerulonephritis\n'
                      '   - Interstitial nephritis\n'
                      '3. Postrenal - Obstruction of urine flow:\n'
                      '   - Kidney stones\n'
                      '   - Enlarged prostate\n'
                      '   - Tumors',
            'prevention': 'Prevention measures include:\n'
                         '- Stay hydrated\n'
                         '- Avoid nephrotoxic drugs (NSAIDs)\n'
                         '- Manage chronic conditions\n'
                         '- Monitor kidney function during illness\n'
                         '- Avoid contrast dyes when possible in high-risk patients'
        },
        'kidney-stones': {
            'name': 'Kidney Stones',
            'description': 'Kidney stones (renal lithiasis) are hard deposits made of minerals and salts that form inside your kidneys. They can affect any part of your urinary tract and cause severe pain when passing.',
            'stages': 'Stone formation process:\n'
                      '1. Supersaturation - Urine contains more crystal-forming substances\n'
                      '2. Nucleation - Crystal formation begins\n'
                      '3. Growth - Crystals enlarge\n'
                      '4. Aggregation - Crystals clump together\n'
                      '5. Retention - Stones become trapped in kidney',
            'symptoms': 'Common symptoms include:\n'
                        '- Severe pain in side and back, below ribs\n'
                        '- Pain radiating to lower abdomen and groin\n'
                        '- Pain during urination\n'
                        '- Pink, red or brown urine\n'
                        '- Cloudy or foul-smelling urine\n'
                        '- Nausea and vomiting\n'
                        '- Persistent urge to urinate',
            'causes': 'Types and causes:\n'
                      '1. Calcium stones - Most common, usually calcium oxalate\n'
                      '2. Uric acid stones - Form in chronically dehydrated people\n'
                      '3. Struvite stones - Form due to infections\n'
                      '4. Cystine stones - Hereditary disorder causing cystine buildup\n'
                      'Risk factors include dehydration, diet, obesity, digestive diseases, and certain supplements',
            'prevention': 'Prevention strategies:\n'
                         '- Drink 2.5-3 liters of water daily\n'
                         '- Reduce oxalate-rich foods (spinach, nuts, chocolate)\n'
                         '- Limit salt intake\n'
                         '- Reduce animal protein\n'
                         '- Continue eating calcium-rich foods but with meals\n'
                         '- Consider preventive medication if prone to recurrent stones'
        },
        'esrd': {
            'name': 'End-Stage Renal Disease (ESRD)',
            'description': 'End-Stage Renal Disease is the final, irreversible stage of chronic kidney disease where kidney function declines below 10-15% of normal capacity. At this point, kidneys cannot remove toxins, maintain electrolyte balance, or regulate fluid status, making renal replacement therapy (dialysis or transplantation) essential for survival.',
            'stages': 'ESRD care milestones typically include:\n'
                      '1. Late Stage 4 CKD (eGFR 15-29) – accelerated decline, dialysis education\n'
                      '2. Dialysis Readiness – vascular access (AV fistula) or peritoneal catheter placement\n'
                      '3. Initiation of Renal Replacement – hemodialysis, peritoneal dialysis, or CRRT\n'
                      '4. Transplant Evaluation – listing, donor workup, immunologic matching\n'
                      '5. Long-term Management – infection prevention, nutrition, anemia and bone disease control',
            'symptoms': 'Common ESRD manifestations include:\n'
                        '- Persistent nausea, vomiting, metallic taste\n'
                        '- Severe fatigue, cognitive slowing, sleep disturbances\n'
                        '- Generalized pruritus, dry skin, muscle cramps\n'
                        '- Shortness of breath, pleural effusions, pulmonary edema\n'
                        '- Refractory hypertension, fluid overload, weight gain\n'
                        '- Decreased or absent urine output, foamy or bloody urine\n'
                        '- Restless legs, peripheral neuropathy, cold intolerance',
            'causes': 'ESRD most often results from progressive chronic kidney insults such as:\n'
                      '- Long-standing diabetes mellitus (diabetic nephropathy)\n'
                      '- Chronic uncontrolled hypertension\n'
                      '- Polycystic kidney disease and other hereditary disorders\n'
                      '- Recurrent glomerulonephritis or interstitial nephritis\n'
                      '- Autoimmune diseases (lupus nephritis, IgA nephropathy)\n'
                      '- Obstructive uropathy, reflux nephropathy, chronic infections\n'
                      '- Prolonged exposure to nephrotoxic medications or heavy metals',
            'prevention': 'While ESRD cannot be reversed, progression and complications can be managed by:\n'
                          '- Tight blood pressure, glucose, and lipid control to slow remaining nephron loss\n'
                          '- Early referral for dialysis modality education and access placement\n'
                          '- Adhering to dialysis prescription and maintaining dry weight targets\n'
                          '- Following renal diet (low sodium, potassium, phosphorus; individualized protein)\n'
                          '- Treating anemia, mineral bone disease, and metabolic acidosis per KDIGO guidelines\n'
                          '- Staying vaccination up-to-date (hepatitis B, influenza, pneumococcal)\n'
                          '- Pursuing kidney transplant evaluation and living donor options when eligible'
        },
        'glomerulonephritis': {
            'name': 'Glomerulonephritis',
            'description': 'Glomerulonephritis is inflammation of the glomeruli, the tiny filters in your kidneys that remove excess fluid, electrolytes and waste from your bloodstream and pass them into your urine.',
            'stages': 'Classification includes:\n'
                      'Acute: Sudden onset, often post-infectious\n'
                      'Rapidly progressive: Quick deterioration of kidney function\n'
                      'Chronic: Long-term inflammation leading to scarring\n'
                      'Nephrotic syndrome: Heavy proteinuria with edema\n'
                      'Nephritic syndrome: Blood in urine with hypertension',
            'symptoms': 'Signs and symptoms may include:\n'
                        '- Pink or cola-colored urine (hematuria)\n'
                        '- Foamy urine (proteinuria)\n'
                        '- High blood pressure\n'
                        '- Fluid retention (edema) in face, hands, feet and abdomen\n'
                        '- Fatigue\n'
                        '- Headache\n'
                        '- Frequent urination',
            'causes': 'Causes include:\n'
                      'Primary (kidney-specific):\n'
                      '   - Minimal change disease\n'
                      '   - Focal segmental glomerulosclerosis\n'
                      '   - Membranous nephropathy\n'
                      'Secondary (systemic diseases):\n'
                      '   - Diabetes\n'
                      '   - Lupus\n'
                      '   - Vasculitis\n'
                      'Infections:\n'
                      '   - Streptococcal infection\n'
                      '   - Viral infections\n'
                      'Autoimmune disorders',
            'prevention': 'While many causes can\'t be prevented, you can:\n'
                         '- Treat infections promptly\n'
                         '- Control blood pressure and blood sugar\n'
                         '- Avoid nephrotoxic substances\n'
                         '- Get regular checkups to detect early changes\n'
                         '- Follow treatment plans for autoimmune conditions'
        },
        'nephrotic-syndrome': {
            'name': 'Nephrotic Syndrome',
            'description': 'Nephrotic syndrome is a kidney disorder that causes your body to excrete too much protein in your urine. It\'s characterized by severe proteinuria, hypoalbuminemia, edema, and hyperlipidemia.',
            'stages': 'Progression typically follows:\n'
                      '1. Initial proteinuria (>3.5g/day)\n'
                      '2. Hypoalbuminemia (<3.0 g/dL)\n'
                      '3. Edema formation\n'
                      '4. Hyperlipidemia development\n'
                      '5. Increased risk of thromboembolism and infections',
            'symptoms': 'Key symptoms include:\n'
                        '- Severe swelling (edema), particularly in legs, feet and ankles\n'
                        '- Weight gain due to fluid retention\n'
                        '- Fatigue\n'
                        '- Foamy urine due to excess protein\n'
                        '- Loss of appetite\n'
                        '- Pleural effusion (fluid around lungs)\n'
                        '- Increased susceptibility to infections',
            'causes': 'Two main categories:\n'
                      'Primary (glomerular diseases):\n'
                      '   - Minimal change disease (most common in children)\n'
                      '   - Focal segmental glomerulosclerosis\n'
                      '   - Membranous nephropathy\n'
                      'Secondary causes:\n'
                      '   - Diabetes\n'
                      '   - Systemic lupus erythematosus\n'
                      '   - Amyloidosis\n'
                      '   - Certain medications\n'
                      '   - Infections (HIV, hepatitis B and C)',
            'prevention': 'Prevention focuses on managing underlying conditions:\n'
                         '- Control blood sugar in diabetes\n'
                         '- Manage autoimmune diseases\n'
                         '- Avoid nephrotoxic drugs\n'
                         '- Treat infections promptly\n'
                         '- Monitor kidney function regularly\n'
                         '- Follow a low-salt, appropriate protein diet'
        },
        'hypertensive-nephropathy': {
            'name': 'Hypertensive Nephropathy',
            'description': 'Hypertensive nephropathy is kidney damage caused by chronic high blood pressure. It\'s both a cause and consequence of hypertension, creating a dangerous cycle that can lead to kidney failure.',
            'stages': 'Progression includes:\n'
                      '1. Early stage - Microalbuminuria\n'
                      '2. Moderate stage - Proteinuria\n'
                      '3. Advanced stage - Reduced GFR\n'
                      '4. End stage - Kidney failure requiring dialysis or transplant',
            'symptoms': 'Often asymptomatic in early stages. Later symptoms:\n'
                        '- Protein in urine\n'
                        '- Elevated blood pressure\n'
                        '- Swelling in legs and ankles\n'
                        '- Fatigue\n'
                        '- Headaches\n'
                        '- Shortness of breath\n'
                        '- Decreased urine output',
            'causes': 'Primary cause is uncontrolled hypertension leading to:\n'
                      '- Damage to small blood vessels in kidneys\n'
                      '- Reduced blood flow to kidney tissue\n'
                      '- Scarring of kidney filtering units\n'
                      '- Progressive loss of kidney function\n'
                      'Risk factors include obesity, diabetes, family history, and older age',
            'prevention': 'Essential prevention measures:\n'
                         '- Maintain blood pressure <130/80 mmHg\n'
                         '- Take prescribed antihypertensive medications\n'
                         '- Follow DASH diet (Dietary Approaches to Stop Hypertension)\n'
                         '- Exercise regularly\n'
                         '- Maintain healthy weight\n'
                         '- Limit sodium intake\n'
                         '- Avoid excessive alcohol\n'
                         '- Regular kidney function monitoring'
        },
        'renal-osteodystrophy': {
            'name': 'Renal Osteodystrophy',
            'description': 'Renal osteodystrophy is a bone disease that occurs when your kidneys fail to maintain proper levels of calcium and phosphorus in your blood. It\'s a common complication of chronic kidney disease, affecting up to 90% of dialysis patients.',
            'stages': 'Progression correlates with CKD stages:\n'
                      'Stage 3 CKD: Early biochemical changes\n'
                      'Stage 4 CKD: Bone turnover abnormalities\n'
                      'Stage 5 CKD: Severe bone and mineral disorders\n'
                      'With dialysis: Advanced bone disease with fractures',
            'symptoms': 'Symptoms may include:\n'
                        '- Bone pain\n'
                        '- Joint pain\n'
                        '- Muscle weakness\n'
                        '- Fractures\n'
                        '- Itching\n'
                        '- Calcification of blood vessels\n'
                        '- Growth retardation in children',
            'causes': 'Results from:\n'
                      '- Impaired vitamin D activation\n'
                      '- Phosphorus retention\n'
                      '- Calcium imbalance\n'
                      '- Secondary hyperparathyroidism\n'
                      '- Aluminum toxicity (from dialysate or medications)\n'
                      '- Metabolic acidosis',
            'prevention': 'Management strategies:\n'
                         '- Control phosphorus levels with diet and binders\n'
                         '- Maintain adequate calcium intake\n'
                         '- Use active vitamin D analogs\n'
                         '- Monitor parathyroid hormone levels\n'
                         '- Regular bone density testing\n'
                         '- Appropriate dialysis prescription\n'
                         '- Parathyroidectomy when indicated'
        }
    }
    
    disease_data = disease_info.get(disease_id)
    
    if not disease_data:
        disease_name = disease_id.replace('-', ' ').title()
        return render_template('disease_detail.html', disease_id=disease_id, disease_name=disease_name, disease_data=None)
    
    return render_template('disease_detail.html', disease_id=disease_id, disease_name=disease_data['name'], disease_data=disease_data)

@app.route('/api/patient-trends/<username>')
@login_required
def patient_trends(username):
    if current_user.username != username and not current_user.is_doctor():
        return jsonify({'error': 'Access denied'}), 403
    
    patient_data = get_patient_records(username)
    
    if not patient_data or 'history' not in patient_data:
        return jsonify({'error': 'No data available'}), 404
    
    history = patient_data['history']
    
    dates = [record['date'] for record in reversed(history)]
    creatinine = [record['serum_creatinine'] for record in reversed(history)]
    egfr = [record['egfr'] for record in reversed(history)]
    blood_urea = [record['blood_urea'] for record in reversed(history)]
    hemoglobin = [record['hemoglobin'] for record in reversed(history)]
    
    return jsonify({
        'dates': dates,
        'creatinine': creatinine,
        'egfr': egfr,
        'blood_urea': blood_urea,
        'hemoglobin': hemoglobin
    })

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')

# Vercel requires this for the serverless function
def main():
    """Entry point for the application."""
    return app

# Add Vercel handler function
def handler(event, context):
    return app(event, context)

# For local development
if __name__ == '__main__':
    try:
        app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)), debug=True)
    except KeyboardInterrupt:
        print("Shutting down gracefully...")
    except SystemExit:
        # This is normal during Flask reloading
        pass
    finally:
        # Ensure cleanup
        try:
            cleanup()
        except NameError:
            # cleanup function may not be available during reload
            pass
        except Exception as e:
            print(f"Warning: Error during cleanup: {e}")

@app.route('/patient/intake')
@login_required
def patient_intake():
    """Display the patient intake form"""
    if current_user.is_doctor():
        flash('This page is for patients only', 'warning')
        return redirect(url_for('doctor_dashboard'))
    
    return render_template('patient_intake.html')

@app.route('/patient/intake/submit', methods=['POST'])
@login_required
def submit_patient_intake():
    """Process and save patient intake form data"""
    if current_user.is_doctor():
        return jsonify({'error': 'Access denied'}), 403
    
    try:
        # Collect form data
        patient_data = {
            'patient_id': f"P{current_user.id}",
            'patient_name': request.form.get('full_name'),
            'username': current_user.username,
            'age': int(request.form.get('age', 0)),
            'gender': request.form.get('gender'),
            'blood_type': request.form.get('blood_type', 'N/A'),
            'phone': request.form.get('phone'),
            'email': request.form.get('email'),
            'address': request.form.get('address', ''),
            
            # Emergency contact
            'emergency_contact': {
                'name': request.form.get('emergency_contact_name', ''),
                'phone': request.form.get('emergency_contact_phone', ''),
                'relationship': request.form.get('emergency_contact_relationship', '')
            },
            
            # Medical history
            'hypertension': 1 if request.form.get('hypertension') else 0,
            'diabetes_mellitus': 1 if request.form.get('diabetes_mellitus') else 0,
            'coronary_artery_disease': 1 if request.form.get('coronary_artery_disease') else 0,
            'anemia': 1 if request.form.get('anemia') else 0,
            'current_medications': request.form.get('current_medications', ''),
            'allergies': request.form.get('allergies', ''),
            'family_history_kidney': request.form.get('family_history_kidney', 'No'),
            'previous_surgeries': request.form.get('previous_surgeries', ''),
            
            # Lab values
            'bp_systolic': float(request.form.get('bp_systolic')) if request.form.get('bp_systolic') else None,
            'bp_diastolic': float(request.form.get('bp_diastolic')) if request.form.get('bp_diastolic') else None,
            'serum_creatinine': float(request.form.get('serum_creatinine')) if request.form.get('serum_creatinine') else None,
            'blood_urea': float(request.form.get('blood_urea')) if request.form.get('blood_urea') else None,
            'egfr': float(request.form.get('egfr')) if request.form.get('egfr') else None,
            'hemoglobin': float(request.form.get('hemoglobin')) if request.form.get('hemoglobin') else None,
            'blood_glucose': float(request.form.get('blood_glucose')) if request.form.get('blood_glucose') else None,
            'sodium': float(request.form.get('sodium')) if request.form.get('sodium') else None,
            'potassium': float(request.form.get('potassium')) if request.form.get('potassium') else None,
            'specific_gravity': float(request.form.get('specific_gravity')) if request.form.get('specific_gravity') else None,
            'albumin': float(request.form.get('albumin')) if request.form.get('albumin') else None,
            'sugar': float(request.form.get('sugar')) if request.form.get('sugar') else None,
            
            # Lifestyle
            'smoking': request.form.get('smoking', 'Never'),
            'alcohol': request.form.get('alcohol', 'None'),
            'exercise_frequency': request.form.get('exercise_frequency', 'None'),
            'water_intake': request.form.get('water_intake', '4-6 glasses'),
            'sleep_hours': int(request.form.get('sleep_hours')) if request.form.get('sleep_hours') else None,
            
            # Symptoms
            'symptoms': {
                'fatigue': 1 if request.form.get('symptom_fatigue') else 0,
                'pedal_edema': 1 if request.form.get('symptom_swelling') else 0,
                'urination_changes': 1 if request.form.get('symptom_urination') else 0,
                'appetite_loss': 1 if request.form.get('symptom_appetite') else 0,
                'nausea': 1 if request.form.get('symptom_nausea') else 0,
                'sleep_issues': 1 if request.form.get('symptom_sleep') else 0
            },
            'additional_comments': request.form.get('additional_comments', ''),
            
            # Set pedal_edema for ML model
            'pedal_edema': 1 if request.form.get('symptom_swelling') else 0,
            'appetite': 0 if request.form.get('symptom_appetite') else 1,  # Inverted: 0 = poor, 1 = good
        }
        
        # Calculate CKD risk if we have necessary lab values
        if patient_data['serum_creatinine'] and patient_data['blood_urea']:
            from models.ckd_model import ckd_model
            
            # Prepare data for ML model (fill missing values with defaults)
            ml_data = {
                'age': patient_data['age'],
                'bp_systolic': patient_data['bp_systolic'] or 120,
                'bp_diastolic': patient_data['bp_diastolic'] or 80,
                'specific_gravity': patient_data['specific_gravity'] or 1.020,
                'albumin': patient_data['albumin'] or 0,
                'sugar': patient_data['sugar'] or 0,
                'red_blood_cells': 1,  # Default normal
                'pus_cell': 0,  # Default normal
                'bacteria': 0,  # Default normal
                'blood_glucose': patient_data['blood_glucose'] or 100,
                'blood_urea': patient_data['blood_urea'],
                'serum_creatinine': patient_data['serum_creatinine'],
                'sodium': patient_data['sodium'] or 140,
                'potassium': patient_data['potassium'] or 4.5,
                'hemoglobin': patient_data['hemoglobin'] or 14,
                'packed_cell_volume': 44,  # Default
                'white_blood_cell_count': 8000,  # Default
                'red_blood_cell_count': 5,  # Default
                'hypertension': patient_data['hypertension'],
                'diabetes_mellitus': patient_data['diabetes_mellitus'],
                'coronary_artery_disease': patient_data['coronary_artery_disease'],
                'appetite': patient_data['appetite'],
                'pedal_edema': patient_data['pedal_edema'],
                'anemia': patient_data['anemia']
            }
            
            # Get prediction
            prediction = ckd_model.predict_risk(ml_data)
            patient_data.update(prediction)
        else:
            # Set default risk assessment
            patient_data['risk_level'] = 'Unknown'
            patient_data['risk_percentage'] = 0
            patient_data['stage'] = 'N/A'
        
        # Save to database
        save_patient_record(current_user.username, patient_data)
        
        flash('Your medical information has been saved successfully!', 'success')
        return redirect(url_for('patient_dashboard'))
        
    except Exception as e:
        flash(f'Error saving intake data: {str(e)}', 'danger')
        return redirect(url_for('patient_intake'))
