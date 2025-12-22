# VOIS CKD - AI-Powered Chronic Kidney Disease Diagnostic System

## 📋 Project Overview

**VOIS CKD** (Voice of Intelligent Healthcare System for Chronic Kidney Disease) is a comprehensive AI-powered web application designed for early detection, monitoring, and management of kidney-related diseases. The system provides personalized health recommendations, connects patients with doctors, and offers 24/7 AI chatbot support.

---

## 🎯 Problem Statement

### The Challenge

Chronic Kidney Disease (CKD) affects approximately **10% of the global population**, with many cases going undiagnosed until advanced stages. Key challenges include:

1. **Late Detection**: CKD is often called a "silent disease" as it shows no symptoms in early stages
2. **Complex Lab Reports**: Patients struggle to understand medical terminology and lab values
3. **Limited Access to Specialists**: Nephrologists are scarce in many regions
4. **Lack of Personalized Guidance**: Generic health advice doesn't account for individual patient conditions
5. **Medication Management**: CKD patients often take multiple medications that require careful monitoring
6. **Poor Lifestyle Adherence**: Patients lack specific dietary and lifestyle guidance for their condition

### Impact

- **850 million people worldwide** suffer from kidney disease
- **2.4 million deaths annually** attributed to CKD
- CKD is projected to become the **5th leading cause of death by 2040**
- Early detection can slow disease progression by **50-60%**

---

## 💡 Solution

### VOIS CKD - An Integrated Healthcare Platform

Our solution addresses these challenges through a multi-faceted approach:

#### 1. **AI-Powered Lab Report Analysis**
- Upload PDF/Image lab reports for instant analysis
- Automatic extraction of key biomarkers (eGFR, Creatinine, BUN, etc.)
- Multi-disease detection: CKD, Kidney Stones, AKI (Acute Kidney Injury), ESRD

#### 2. **Machine Learning Disease Prediction**
- Trained ML models for each kidney condition
- Stage classification (CKD Stages 1-5)
- Risk level assessment (Low, Moderate, High)
- Evidence-based recommendations

#### 3. **AI Health Assistant (Chatbot)**
- 24/7 patient support powered by Google Gemini AI
- Answers questions about CKD stages, symptoms, terminology
- Personalized responses based on patient data

#### 4. **Doctor-Patient Portal**
- Appointment booking with Google Meet integration
- Real-time messaging between doctors and patients
- Prescription management with AI analysis
- Patient intake forms for comprehensive data collection

#### 5. **Personalized Lifestyle Recommendations**
- AI-generated diet plans specific to CKD stage
- Exercise recommendations
- Medication guidance
- Weekly meal plans

---

## 🛠️ Technology Stack

### Backend
| Technology | Purpose |
|------------|---------|
| **Python 3.11** | Core programming language |
| **Flask 3.0** | Web framework |
| **Flask-Login** | User authentication & session management |
| **MongoDB** | NoSQL database for patient records |
| **PyMongo** | MongoDB Python driver |

### Machine Learning
| Technology | Purpose |
|------------|---------|
| **Scikit-learn** | ML models for disease prediction |
| **Pandas/NumPy** | Data processing and manipulation |
| **Joblib** | Model serialization |
| **Google Gemini AI** | AI recommendations & chatbot |

### Frontend
| Technology | Purpose |
|------------|---------|
| **HTML5/CSS3** | Structure and styling |
| **JavaScript** | Interactive features |
| **Chart.js** | Health trend visualizations |
| **Driver.js** | Welcome tour for new users |
| **Font Awesome** | Icons |

### Document Processing
| Technology | Purpose |
|------------|---------|
| **PyPDF2** | PDF text extraction |
| **FPDF2** | PDF report generation |

### Deployment
| Technology | Purpose |
|------------|---------|
| **Vercel** | Serverless deployment |
| **Replit** | Development environment |

---

## 📁 Project Structure

```
Vois_CKD/
├── app.py                    # Main Flask application (3300+ lines)
├── init_database.py          # Database initialization scripts
├── requirements.txt          # Python dependencies
├── setup.py                  # Package configuration
├── vercel.json              # Vercel deployment config
│
├── models/                   # ML Models & Business Logic
│   ├── disease_predictor.py  # Multi-disease prediction engine
│   ├── ckd_model.py          # CKD-specific model
│   ├── kidney_stone_model.py # Kidney stone detection
│   ├── ai_recommender.py     # Gemini AI integration
│   ├── patient_chatbot.py    # 24/7 AI chatbot
│   ├── pdf_parser.py         # Lab report extraction
│   ├── prescription_report_generator.py  # PDF report generation
│   ├── database.py           # MongoDB connection
│   ├── user.py               # User & patient data models
│   ├── ckd_model.pkl         # Trained CKD model
│   ├── aki_detection_model.pkl    # Trained AKI model
│   ├── esrd_detection_model.pkl   # Trained ESRD model
│   └── kidney_stone_yolo_model.pt # YOLO model for stone detection
│
├── templates/                # HTML Templates (32 files)
│   ├── patient_dashboard.html    # Main patient interface
│   ├── doctor_dashboard.html     # Doctor's interface
│   ├── admin_dashboard.html      # Admin panel
│   ├── lab_analysis.html         # Lab report upload
│   ├── ai_lifestyle_plan.html    # AI recommendations
│   ├── prescriptions.html        # Prescription management
│   ├── appointments.html         # Appointment booking
│   └── ... (25 more templates)
│
├── static/                   # Static Assets
│   ├── css/                  # Stylesheets
│   ├── images/               # Images & avatars
│   ├── reports/              # Generated PDF reports
│   └── uploads/              # Uploaded lab reports
│
└── uploads/                  # User file uploads
```

---

## ✅ Current Progress

### Completed Features

#### User Management
- [x] Patient registration with comprehensive medical history
- [x] Doctor registration (admin-controlled)
- [x] Admin dashboard for system management
- [x] Role-based access control (Patient, Doctor, Admin)
- [x] Welcome tour for new users

#### Patient Features
- [x] Personal health dashboard with key metrics
- [x] Lab report upload and AI analysis (PDF/Images)
- [x] Multi-disease detection (CKD, Kidney Stone, AKI, ESRD)
- [x] Health trend visualization (Charts)
- [x] Disease-specific detail pages
- [x] Report history tracking
- [x] AI chatbot for 24/7 support
- [x] Doctor booking with location-based recommendations
- [x] Prescription viewing

#### Doctor Features
- [x] Patient list management
- [x] Detailed patient health records
- [x] Prescription creation
- [x] Appointment management
- [x] Video consultation via Google Meet
- [x] AI-assisted prescription analysis

#### AI/ML Features
- [x] CKD stage prediction model
- [x] AKI detection model
- [x] ESRD prediction model
- [x] Kidney stone detection
- [x] AI-powered lifestyle recommendations (Gemini)
- [x] Prescription analysis with recommendations
- [x] PDF report generation

#### Technical Features
- [x] MongoDB database integration
- [x] HIPAA-compliant data handling
- [x] PDF parsing and text extraction
- [x] Responsive design (mobile-friendly)
- [x] Dark mode support (for chatbot)

---

## 🚀 Future Scope

### Phase 1: Enhanced AI Capabilities
- [ ] **Kidney Stone Image Analysis**: Integrate YOLO model for CT/Ultrasound image analysis
- [ ] **Voice Input**: Allow patients to describe symptoms via voice
- [ ] **Multi-language Support**: Hindi, Marathi, Tamil, etc.
- [ ] **Predictive Analytics**: Predict disease progression over time

### Phase 2: Advanced Features
- [ ] **Wearable Integration**: Connect with smartwatches for real-time vitals
- [ ] **Medication Reminders**: Push notifications for medications
- [ ] **Family Member Access**: Allow caregivers to monitor patients
- [ ] **Emergency Alerts**: Auto-alert doctors for critical readings

### Phase 3: Scale & Integration
- [ ] **Hospital Integration**: Connect with hospital EMR systems
- [ ] **Insurance Integration**: Share reports with insurance providers
- [ ] **Pharmacy Network**: Direct prescription fulfillment
- [ ] **Telemedicine Enhancement**: In-app video calls (no Google Meet)

### Phase 4: Research & Analytics
- [ ] **Population Health Analytics**: Aggregate anonymized data for research
- [ ] **Clinical Trial Matching**: Connect patients with relevant trials
- [ ] **Outcome Tracking**: Long-term patient outcome monitoring
- [ ] **AI Model Improvement**: Continuous learning from new data

---

## 📊 Key Metrics & Achievements

| Metric | Value |
|--------|-------|
| Total Lines of Code | ~15,000+ |
| Flask Routes | 80+ |
| HTML Templates | 32 |
| ML Models | 4 (CKD, AKI, ESRD, Kidney Stone) |
| Database Collections | 5+ |

---

## 🔐 Security & Compliance

- **HIPAA Compliance**: PII is anonymized before AI processing
- **Password Hashing**: Werkzeug security for password storage
- **Session Management**: Flask-Login for secure sessions
- **Environment Variables**: Sensitive keys stored in `.env`
- **Input Validation**: Server-side validation for all forms

---

## 👥 User Roles

### Patient
- View personal health dashboard
- Upload and analyze lab reports
- Chat with AI assistant
- Book appointments with doctors
- View prescriptions and recommendations

### Doctor
- Manage assigned patients
- View patient health records and trends
- Create prescriptions
- Schedule appointments
- Conduct video consultations

### Admin
- Add/manage doctors
- View all patients
- Access system feedback
- Monitor platform usage

---

## 🏃 How to Run

```bash
# 1. Clone the repository
git clone <repository-url>
cd Vois_CKD

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set environment variables
cp .env.example .env
# Edit .env with your MongoDB URI and Gemini API key

# 5. Initialize database
python init_database.py

# 6. Run the application
python app.py

# 7. Access at http://localhost:5000
```

---

## 📝 Demo Credentials

| Role | Username | Password |
|------|----------|----------|
| Patient | patient1 | patient123 |
| Doctor | doctor1 | doctor123 |
| Admin | admin | admin123 |

---

## 📧 Contact

For questions or support, please contact the development team.

---

*Last Updated: December 22, 2025*
