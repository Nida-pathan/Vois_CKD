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
            flash('All fields are required', 'danger')
            return render_template('register.html')
        
        if password != confirm_password:
            flash('Passwords do not match', 'danger')
            return render_template('register.html')
        
        if User.get_by_username(username):
            flash('Username already exists', 'danger')
            return render_template('register.html')
        
        # Create new patient user
        User.create_user(username, password, 'patient', email)
        
        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('login'))
        
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

@app.route('/doctor/login', methods=['GET', 'POST'])
def doctor_login():
    if current_user.is_authenticated:
        if current_user.is_doctor():
            return redirect(url_for('doctor_dashboard'))
        else:
            flash('You are logged in as a patient. Please logout first.', 'warning')
            return redirect(url_for('patient_portal'))
    
    if request.method == 'POST':
        username = request.form.get('username') or ''
        password = request.form.get('password') or ''
        
        user = User.get_by_username(username)
        
        if user and password and check_password_hash(user.password_hash, password):
            if user.is_doctor():
                login_user(user)
                flash(f'Welcome, Dr. {user.username}!', 'success')
                return redirect(url_for('doctor_dashboard'))
            else:
                flash('This login is for healthcare professionals only. Please use the Patient Login.', 'danger')
        else:
            flash('Invalid username or password', 'danger')
    
    return render_template('doctor_login.html')

@app.route('/patient/login', methods=['GET', 'POST'])
def patient_login():
    if current_user.is_authenticated:
        if current_user.is_patient():
            return redirect(url_for('patient_portal'))
        else:
            flash('You are logged in as a doctor. Please logout first.', 'warning')
            return redirect(url_for('doctor_dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username') or ''
        password = request.form.get('password') or ''
        
        if username:
            user = User.get_by_username(username)
        else:
            user = None
        
        if user and password and check_password_hash(user.password_hash, password):
            if user.is_patient():
                login_user(user)
                flash(f'Welcome, {user.username}!', 'success')
                return redirect(url_for('patient_portal'))
            else:
                flash('This login is for patients only. Please use the Doctor Login.', 'danger')
        else:
            flash('Invalid username or password', 'danger')
    
    return render_template('patient_login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('landing'))

# Admin Routes
@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    # Default admin credentials
    ADMIN_ID = 'admin'
    ADMIN_PASSWORD = 'admin123'
    
    if request.method == 'POST':
        admin_id = request.form.get('admin_id')
        admin_password = request.form.get('admin_password')
        
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

@app.route('/doctor/dashboard')
@login_required
def doctor_dashboard():
    if not current_user.is_doctor():
        flash('Access denied. Doctors only.', 'danger')
        return redirect(url_for('patient_portal'))
    
    all_patients_data = get_all_patients_data()
    all_patients = []
    for data in all_patients_data:
        all_patients.append({
            'patient_id': data.get('patient_id'),
            'name': data.get('patient_name', 'Unknown'),
            'risk_percentage': data.get('risk_percentage', 0),
            'stage': data.get('stage', 'N/A'),
            'risk_level': data.get('risk_level', 'Unknown'),
            'age': data.get('age', 'N/A'),
            'egfr': data.get('egfr', 'N/A')
        })
    
    return render_template('doctor_dashboard.html', patients=all_patients)

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
    patient_data = get_patient_data(patient_id)
    
    if not patient_data:
        # Try to find in patient records
        records = get_patient_records(current_user.username)
        if records and records.get('patient_id') == patient_id:
            patient_data = records
    
    if not patient_data:
        flash('Patient not found', 'danger')
        return redirect(url_for('doctor_dashboard'))
    
    return render_template('results.html', patient=patient_data)

@app.route('/patient/portal')
@login_required
def patient_portal():
    if current_user.is_doctor():
        return redirect(url_for('doctor_dashboard'))
    
    # Redirect to the new patient dashboard
    return redirect(url_for('patient_dashboard'))

@app.route('/patient/dashboard')
@login_required
def patient_dashboard():
    if current_user.is_doctor():
        return redirect(url_for('doctor_dashboard'))
    
    # Get patient records
    patient_data = get_patient_records(current_user.username)
    
    # Get patient trial information
    patient_trials = get_patient_trials(current_user.username)
    
    # Get available doctors
    doctors_list = get_all_doctors()
    available_doctors = []
    for doc in doctors_list:
        available_doctors.append({
            'name': f"Dr. {doc.username}",
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
    
    return render_template('patient_dashboard.html', 
                         patient=patient_data, 
                         trials=patient_trials,
                         doctors=available_doctors,
                         dashboard=dashboard_data)

@app.route('/patient/upload-lab', methods=['POST'])
@login_required
def upload_lab_report():
    if current_user.is_doctor():
        return jsonify({'error': 'Access denied'}), 403
    
    # Check if patient has free trials remaining
    trials = get_patient_trials(current_user.username)
    
    if trials['remaining'] <= 0:
        return jsonify({'error': 'No free trials remaining. Please upgrade to continue.'}), 400
    
    # Handle file upload (simplified for now)
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    # Update trial count
    new_remaining = trials['remaining'] - 1
    new_used = trials['used'] + 1
    update_patient_trials(current_user.username, new_remaining, new_used)
    
    # Process the lab report (simplified - would integrate with actual ML model)
    try:
        if file.filename.endswith('.csv'):
            df = pd.read_csv(file)
            # Process CSV data
            results = {'status': 'success', 'message': 'Lab report analyzed successfully', 'data_points': len(df)}
        else:
            # For PDF/Excel files, would need additional processing
            results = {'status': 'success', 'message': 'Lab report uploaded successfully', 'file_type': file.filename.split('.')[-1]}
        
        return jsonify(results)
    
    except Exception as e:
        return jsonify({'error': f'Error processing file: {str(e)}'}), 500

@app.route('/patient/book-appointment', methods=['POST'])
@login_required
def book_appointment():
    if current_user.is_doctor():
        return jsonify({'error': 'Access denied'}), 403
    
    data = request.get_json()
    doctor_name = data.get('doctor_name')
    preferred_date = data.get('preferred_date')
    preferred_time = data.get('preferred_time')
    
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
    
    return jsonify({
        'status': 'success', 
        'message': f'Appointment request sent to {doctor_name}. You will be notified shortly.',
        'appointment': appointment
    })

@app.route('/modern-dashboard')
def modern_dashboard():
    return render_template('modern_dashboard.html')

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
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)), debug=True)# Patient Intake Form Routes
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
