from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash, generate_password_hash
from models.user import User, users_db, patients_data, patient_records
from models.ckd_model import ckd_model
import pandas as pd
import io
import os

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

@app.route('/')
def index():
    if current_user.is_authenticated:
        if current_user.is_doctor():
            return redirect(url_for('doctor_dashboard'))
        else:
            return redirect(url_for('patient_portal'))
    return redirect(url_for('landing'))

@app.route('/landing')
def landing():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    return render_template('landing.html')

@app.route('/login')
def login():
    return redirect(url_for('landing'))

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
            'risk_level': data.get('risk_level', 'Unknown')
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

@app.route('/doctor/upload-csv', methods=['POST'])
@login_required
def upload_csv():
    if not current_user.is_doctor():
        return jsonify({'error': 'Access denied'}), 403
    
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if file and file.filename and file.filename.endswith('.csv'):
        try:
            df = pd.read_csv(io.StringIO(file.stream.read().decode('utf-8')))
            
            patient_list = df.to_dict('records')
            results = ckd_model.predict_batch(patient_list)
            
            for result in results:
                patient_id = result.get('patient_id', f"AUTO_{len(patients_data) + 1}")
                patients_data[patient_id] = result
            
            flash(f'Successfully processed {len(results)} patients from CSV', 'success')
            return jsonify({'success': True, 'count': len(results)})
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    return jsonify({'error': 'Invalid file format'}), 400

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
    
    patient_data = patient_records.get(current_user.username, {})
    
    if patient_data and 'history' in patient_data:
        latest = patient_data['history'][0]
        prediction_data = {
            'age': patient_data.get('age', 0),
            'gender': patient_data.get('gender', 'male'),
            'serum_creatinine': latest.get('serum_creatinine', 1.0),
            'blood_urea': latest.get('blood_urea', 20),
            'hemoglobin': latest.get('hemoglobin', 14),
            'bp_systolic': latest.get('bp_systolic', 120),
            'bp_diastolic': latest.get('bp_diastolic', 80),
            'specific_gravity': 1.020,
            'albumin': 0,
            'sugar': 0,
            'red_blood_cells': 1,
            'pus_cell': 0,
            'bacteria': 0,
            'blood_glucose': 100,
            'sodium': 140,
            'potassium': 4.5,
            'packed_cell_volume': 44,
            'white_blood_cell_count': 8000,
            'red_blood_cell_count': 5,
            'hypertension': 1 if latest.get('bp_systolic', 120) > 140 else 0,
            'diabetes_mellitus': 0,
            'coronary_artery_disease': 0,
            'appetite': 1,
            'pedal_edema': 0,
            'anemia': 1 if latest.get('hemoglobin', 14) < 12 else 0
        }
        
        prediction = ckd_model.predict_risk(prediction_data)
        patient_data.update(prediction)
    
    return render_template('patient_portal.html', patient=patient_data)

@app.route('/modern-dashboard')
def modern_dashboard():
    return render_template('modern_dashboard.html')

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

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)), debug=True)

# Vercel requires this for the serverless function
def main():
    """Entry point for the application."""
    return app

# For local development
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)), debug=True)
