# CKD Diagnostic and Prediction System

## Overview
An AI-driven diagnostic and prediction system designed to detect Chronic Kidney Disease (CKD) and estimate its progression stages early using clinical and laboratory data. Built with Flask and scikit-learn.

## Current State
MVP implementation with core features:
- User authentication (doctor/patient roles)
- AI-powered CKD risk prediction and stage classification
- Doctor dashboard and patient portal
- Single patient and CSV batch data processing
- Trend visualization for kidney function metrics

## Recent Changes
- **2025-10-30**: Added separate login pages for doctors and patients with landing page
- **2025-10-30**: Initial project setup with Flask, authentication system, ML model, and dashboards

## Project Architecture

### Tech Stack
- **Backend**: Python 3.11, Flask
- **ML Framework**: scikit-learn (Random Forest classifier)
- **Frontend**: HTML, CSS (Bootstrap-inspired), Chart.js for visualizations
- **Authentication**: Flask-Login with session management
- **Data Storage**: In-memory (session-based for MVP)

### Project Structure
```
/
├── app.py                    # Main Flask application
├── models/
│   ├── ckd_model.py         # ML model training and prediction
│   └── user.py              # User authentication models
├── templates/
│   ├── base.html            # Base template
│   ├── landing.html         # Landing page with login options
│   ├── doctor_login.html    # Doctor-specific login page
│   ├── patient_login.html   # Patient-specific login page
│   ├── doctor_dashboard.html
│   ├── patient_portal.html
│   ├── add_patient.html
│   └── results.html
├── static/
│   ├── css/
│   │   └── style.css        # Custom styling
│   └── js/
│       └── charts.js        # Chart.js visualizations
├── requirements.txt
└── replit.md
```

### Key Features
1. **Separate Login System**: 
   - Landing page with two login options
   - Doctor login (teal/green theme) for healthcare professionals
   - Patient login (blue theme) for patients
   - Role-based validation preventing cross-role authentication
2. **Authentication**: Secure password hashing with role-based access control
3. **AI Prediction**: Scikit-learn Random Forest model predicting CKD risk (0-100%) and stage (1-5)
4. **Doctor Dashboard**: Patient management, data input, batch CSV upload
5. **Patient Portal**: Health status display with color-coded risk levels and historical trends
6. **Visualizations**: Interactive trend charts for creatinine, eGFR, and other metrics using Chart.js

### Clinical Parameters Used
- Age, Gender, Blood Pressure (systolic/diastolic)
- Serum Creatinine, Blood Urea, eGFR
- Hemoglobin, Red Blood Cell Count, White Blood Cell Count
- Albumin, Sugar levels
- Specific Gravity, Diabetes Mellitus, Hypertension status

## Access URLs
- **Landing Page**: `/` or `/landing` - Choose between doctor or patient login
- **Doctor Login**: `/doctor/login` - Healthcare professional access
- **Patient Login**: `/patient/login` - Patient portal access
- **Doctor Dashboard**: `/doctor/dashboard` (requires doctor authentication)
- **Patient Portal**: `/patient/portal` (requires patient authentication)

## Demo Credentials
**Doctor Account:**
- Username: doctor1
- Password: doctor123

**Patient Account:**
- Username: patient1
- Password: patient123

## User Preferences
None specified yet.

## Next Phase Features
- PostgreSQL database integration for persistent storage
- Real-time alerting system for abnormal results
- SHAP/feature importance visualization for explainable AI
- Comprehensive historical data tracking
- REST API endpoints for EHR integration
- HIPAA/GDPR compliance infrastructure
- Docker containerization
