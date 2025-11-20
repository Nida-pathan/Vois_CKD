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
    
    return render_template('patient_dashboard.html', 
                         patient=patient_data, 
                         trials=patient_trials,
                         doctors=available_doctors)

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
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)), debug=True)