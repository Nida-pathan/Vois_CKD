from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify, make_response, send_from_directory
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash, generate_password_hash
from models.user import User, users_db, patients_data, patient_records
from models.ckd_model import ckd_model
import pandas as pd
import io
import os

# Track patient free trials for lab uploads
patient_upload_trials = {}

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SESSION_SECRET', 'ckd-diagnostic-system-secret-key-2025')

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'landing'  # type: ignore

@login_manager.user_loader
def load_user(user_id):
    for user in users_db.values():
        if user.id == user_id:
            return user
    return None

@app.route('/test')
def test():
    return "Flask app is working!"

@app.route('/')
def index():
    # Always redirect to landing page
    return redirect(url_for('landing'))

@app.route('/landing')
def landing():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    return render_template('kidneycompanion_landing.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username') or ''
        password = request.form.get('password') or ''
        
        user = users_db.get(username)
        
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
        
        user = users_db.get(username)
        
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
            user = users_db.get(username)
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
    doctors = [user for user in users_db.values() if user.is_doctor()]
    
    # Add patients list to each doctor
    for doctor in doctors:
        doctor.patients = [user for user in users_db.values() if user.is_patient()]
    
    # Mock feedback data (in real app, this would come from database)
    feedbacks = [
        {
            'patient_name': 'John Doe',
            'doctor_name': 'doctor1',
            'rating': 5,
            'comment': 'Excellent service and very professional care.',
            'date': pd.Timestamp('2025-01-15')
        },
        {
            'patient_name': 'Jane Smith',
            'doctor_name': 'doctor1',
            'rating': 4,
            'comment': 'Good experience, doctor was very helpful.',
            'date': pd.Timestamp('2025-01-12')
        }
    ]
    
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
    if username in users_db:
        flash('Username already exists', 'danger')
        return redirect(url_for('admin_dashboard'))
    
    # Create new doctor with proper User model constructor
    doctor_id = str(len(users_db) + 1)
    doctor = User(doctor_id, username, generate_password_hash(password), 'doctor')
    doctor.email = email
    doctor.specialization = specialization
    users_db[username] = doctor
    
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
    
    all_patients = []
    for patient_id, data in patients_data.items():
        all_patients.append({
            'patient_id': patient_id,
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
        
        prediction = ckd_model.predict_risk(patient_data)
        
        patient_data.update(prediction)
        patients_data[patient_data['patient_id']] = patient_data
        
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
    results = ckd_model.predict_batch(patient_list)
    
    for result in results:
        patient_id = result.get('patient_id', f"AUTO_{len(patients_data) + 1}")
        patients_data[patient_id] = result
    
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
    patient_data = patients_data.get(patient_id)
    
    if not patient_data:
        patient_data = patient_records.get(current_user.username, {})
    
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
    
    patient_data = patient_records.get(current_user.username, {})
    
    # Get patient trial information
    patient_trials = patient_upload_trials.get(current_user.username, {'remaining': 2, 'used': 0})
    
    # Get available doctors
    available_doctors = [
        {
            'name': 'Dr. Ramesh Kumar',
            'specialty': 'Nephrologist',
            'experience': '15 years experience',
            'avatar': 'DR'
        },
        {
            'name': 'Dr. Sunita Agarwal',
            'specialty': 'General Physician',
            'experience': '12 years experience',
            'avatar': 'SA'
        },
        {
            'name': 'Dr. Vikram Patel',
            'specialty': 'Ayurvedic Specialist',
            'experience': '20 years experience',
            'avatar': 'VP'
        }
    ]
    
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
    if current_user.username not in patient_upload_trials:
        patient_upload_trials[current_user.username] = {'remaining': 2, 'used': 0}
    
    trials = patient_upload_trials[current_user.username]
    
    if trials['remaining'] <= 0:
        return jsonify({'error': 'No free trials remaining. Please upgrade to continue.'}), 400
    
    # Handle file upload (simplified for now)
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    # Update trial count
    trials['remaining'] -= 1
    trials['used'] += 1
    
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
    
    # In a real implementation, this would be saved to a database
    # For now, just return success message
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

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')

@app.route('/api/patient-trends/<username>')
@login_required
def patient_trends(username):
    if current_user.username != username and not current_user.is_doctor():
        return jsonify({'error': 'Access denied'}), 403
    
    patient_data = patient_records.get(username, {})
    
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
