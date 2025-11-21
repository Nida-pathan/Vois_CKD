#!/usr/bin/env python3
"""
Database Initialization Script for CKD Diagnostic System
Creates all necessary collections and populates with sample data
"""

import os
import sys
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash
from models.database import Database
from bson.objectid import ObjectId

def init_collections():
    """Initialize all MongoDB collections with indexes"""
    print("Initializing database collections...")
    
    db = Database.get_db()
    
    # Create indexes for better performance
    db.users.create_index("username", unique=True)
    db.users.create_index("role")
    
    db.patients_data.create_index("patient_id", unique=True)
    db.patients_data.create_index("doctor_id")
    db.patients_data.create_index("risk_level")
    
    db.appointments.create_index([("doctor", 1), ("date", 1)])
    db.appointments.create_index([("patient", 1), ("date", 1)])
    
    db.prescriptions.create_index("patient_id")
    db.prescriptions.create_index("doctor_id")
    
    db.lab_results.create_index("patient_id")
    db.lab_results.create_index("test_date")
    
    db.messages.create_index([("sender", 1), ("receiver", 1)])
    db.messages.create_index("timestamp")
    
    print("✓ Collections and indexes created")

def create_sample_users():
    """Create sample doctors and patients"""
    print("\nCreating sample users...")
    
    db = Database.get_db()
    
    # Clear existing users (optional - comment out if you want to keep existing)
    # db.users.delete_many({})
    
    # Sample Doctors
    doctors = [
        {
            "username": "doctor1",
            "password_hash": generate_password_hash("doctor123"),
            "role": "doctor",
            "email": "doctor1@ckd.com",
            "specialization": "Nephrologist",
            "patients": [],
            "created_at": datetime.now().isoformat()
        },
        {
            "username": "dr_smith",
            "password_hash": generate_password_hash("smith123"),
            "role": "doctor",
            "email": "dr.smith@ckd.com",
            "specialization": "Nephrologist",
            "patients": [],
            "created_at": datetime.now().isoformat()
        }
    ]
    
    for doctor in doctors:
        if not db.users.find_one({"username": doctor["username"]}):
            db.users.insert_one(doctor)
            print(f"  ✓ Created doctor: {doctor['username']}")
        else:
            print(f"  - Doctor {doctor['username']} already exists")
    
    # Sample Patients (user accounts)
    patients = [
        {
            "username": "john_smith",
            "password_hash": generate_password_hash("patient123"),
            "role": "patient",
            "email": "john.smith@email.com",
            "created_at": datetime.now().isoformat()
        },
        {
            "username": "mary_johnson",
            "password_hash": generate_password_hash("patient123"),
            "role": "patient",
            "email": "mary.johnson@email.com",
            "created_at": datetime.now().isoformat()
        },
        {
            "username": "robert_williams",
            "password_hash": generate_password_hash("patient123"),
            "role": "patient",
            "email": "robert.williams@email.com",
            "created_at": datetime.now().isoformat()
        }
    ]
    
    for patient in patients:
        if not db.users.find_one({"username": patient["username"]}):
            db.users.insert_one(patient)
            print(f"  ✓ Created patient: {patient['username']}")
        else:
            print(f"  - Patient {patient['username']} already exists")

def create_sample_patients_data():
    """Create sample patient medical data"""
    print("\nCreating sample patient medical data...")
    
    db = Database.get_db()
    
    # Sample patient medical records
    patients_data = [
        {
            "patient_id": "P001",
            "patient_name": "John Smith",
            "age": 65,
            "gender": "Male",
            "risk_percentage": 75.5,
            "risk_level": "High",
            "stage": 3,
            "egfr": 45.2,
            "blood_pressure": "140/90",
            "diabetes": True,
            "hypertension": True,
            "hemoglobin": 11.5,
            "serum_creatinine": 2.1,
            "albumin": 3.2,
            "last_updated": datetime.now().isoformat(),
            "doctor_id": "doctor1",
            "contact": "555-0101",
            "email": "john.smith@email.com"
        },
        {
            "patient_id": "P002",
            "patient_name": "Mary Johnson",
            "age": 58,
            "gender": "Female",
            "risk_percentage": 45.3,
            "risk_level": "Moderate",
            "stage": 2,
            "egfr": 68.5,
            "blood_pressure": "130/85",
            "diabetes": False,
            "hypertension": True,
            "hemoglobin": 12.8,
            "serum_creatinine": 1.4,
            "albumin": 3.8,
            "last_updated": datetime.now().isoformat(),
            "doctor_id": "doctor1",
            "contact": "555-0102",
            "email": "mary.johnson@email.com"
        },
        {
            "patient_id": "P003",
            "patient_name": "Robert Williams",
            "age": 72,
            "gender": "Male",
            "risk_percentage": 88.7,
            "risk_level": "Critical",
            "stage": 4,
            "egfr": 22.3,
            "blood_pressure": "155/95",
            "diabetes": True,
            "hypertension": True,
            "hemoglobin": 9.8,
            "serum_creatinine": 3.5,
            "albumin": 2.8,
            "last_updated": datetime.now().isoformat(),
            "doctor_id": "doctor1",
            "contact": "555-0103",
            "email": "robert.williams@email.com"
        },
        {
            "patient_id": "P004",
            "patient_name": "Sarah Davis",
            "age": 52,
            "gender": "Female",
            "risk_percentage": 25.8,
            "risk_level": "Low",
            "stage": 1,
            "egfr": 92.1,
            "blood_pressure": "120/80",
            "diabetes": False,
            "hypertension": False,
            "hemoglobin": 13.5,
            "serum_creatinine": 0.9,
            "albumin": 4.2,
            "last_updated": datetime.now().isoformat(),
            "doctor_id": "doctor1",
            "contact": "555-0104",
            "email": "sarah.davis@email.com"
        },
        {
            "patient_id": "P005",
            "patient_name": "Michael Brown",
            "age": 68,
            "gender": "Male",
            "risk_percentage": 92.3,
            "risk_level": "Critical",
            "stage": 5,
            "egfr": 12.5,
            "blood_pressure": "160/100",
            "diabetes": True,
            "hypertension": True,
            "hemoglobin": 8.2,
            "serum_creatinine": 5.8,
            "albumin": 2.3,
            "last_updated": datetime.now().isoformat(),
            "doctor_id": "doctor1",
            "contact": "555-0105",
            "email": "michael.brown@email.com"
        },
        {
            "patient_id": "P006",
            "patient_name": "Jennifer Wilson",
            "age": 45,
            "gender": "Female",
            "risk_percentage": 35.2,
            "risk_level": "Moderate",
            "stage": 2,
            "egfr": 72.8,
            "blood_pressure": "128/82",
            "diabetes": True,
            "hypertension": False,
            "hemoglobin": 12.2,
            "serum_creatinine": 1.2,
            "albumin": 3.9,
            "last_updated": datetime.now().isoformat(),
            "doctor_id": "dr_smith",
            "contact": "555-0106",
            "email": "jennifer.wilson@email.com"
        },
        {
            "patient_id": "P007",
            "patient_name": "David Martinez",
            "age": 61,
            "gender": "Male",
            "risk_percentage": 68.9,
            "risk_level": "High",
            "stage": 3,
            "egfr": 38.7,
            "blood_pressure": "145/92",
            "diabetes": True,
            "hypertension": True,
            "hemoglobin": 10.8,
            "serum_creatinine": 2.6,
            "albumin": 3.1,
            "last_updated": datetime.now().isoformat(),
            "doctor_id": "dr_smith",
            "contact": "555-0107",
            "email": "david.martinez@email.com"
        },
        {
            "patient_id": "P008",
            "patient_name": "Lisa Anderson",
            "age": 55,
            "gender": "Female",
            "risk_percentage": 52.4,
            "risk_level": "Moderate",
            "stage": 2,
            "egfr": 58.3,
            "blood_pressure": "135/88",
            "diabetes": False,
            "hypertension": True,
            "hemoglobin": 11.9,
            "serum_creatinine": 1.6,
            "albumin": 3.6,
            "last_updated": datetime.now().isoformat(),
            "doctor_id": "doctor1",
            "contact": "555-0108",
            "email": "lisa.anderson@email.com"
        },
        {
            "patient_id": "P009",
            "patient_name": "James Taylor",
            "age": 70,
            "gender": "Male",
            "risk_percentage": 81.2,
            "risk_level": "High",
            "stage": 4,
            "egfr": 25.6,
            "blood_pressure": "150/95",
            "diabetes": True,
            "hypertension": True,
            "hemoglobin": 9.5,
            "serum_creatinine": 3.2,
            "albumin": 2.9,
            "last_updated": datetime.now().isoformat(),
            "doctor_id": "doctor1",
            "contact": "555-0109",
            "email": "james.taylor@email.com"
        },
        {
            "patient_id": "P010",
            "patient_name": "Patricia Thomas",
            "age": 48,
            "gender": "Female",
            "risk_percentage": 18.5,
            "risk_level": "Low",
            "stage": 1,
            "egfr": 95.7,
            "blood_pressure": "118/78",
            "diabetes": False,
            "hypertension": False,
            "hemoglobin": 13.8,
            "serum_creatinine": 0.8,
            "albumin": 4.3,
            "last_updated": datetime.now().isoformat(),
            "doctor_id": "dr_smith",
            "contact": "555-0110",
            "email": "patricia.thomas@email.com"
        }
    ]
    
    for patient_data in patients_data:
        existing = db.patients_data.find_one({"patient_id": patient_data["patient_id"]})
        if not existing:
            db.patients_data.insert_one(patient_data)
            print(f"  ✓ Created patient data: {patient_data['patient_name']} (ID: {patient_data['patient_id']})")
        else:
            print(f"  - Patient data {patient_data['patient_id']} already exists")

def create_sample_appointments():
    """Create sample appointments"""
    print("\nCreating sample appointments...")
    
    db = Database.get_db()
    
    today = datetime.now()
    
    appointments = [
        {
            "patient": "john_smith",
            "patient_name": "John Smith",
            "doctor": "doctor1",
            "date": (today + timedelta(days=2)).strftime("%Y-%m-%d"),
            "time": "10:00 AM",
            "type": "Follow-up",
            "status": "Scheduled",
            "notes": "Regular checkup for CKD Stage 3"
        },
        {
            "patient": "robert_williams",
            "patient_name": "Robert Williams",
            "doctor": "doctor1",
            "date": (today + timedelta(days=1)).strftime("%Y-%m-%d"),
            "time": "2:00 PM",
            "type": "Urgent",
            "status": "Scheduled",
            "notes": "Critical - Stage 4 CKD monitoring"
        },
        {
            "patient": "mary_johnson",
            "patient_name": "Mary Johnson",
            "doctor": "doctor1",
            "date": (today + timedelta(days=5)).strftime("%Y-%m-%d"),
            "time": "11:30 AM",
            "type": "Routine",
            "status": "Scheduled",
            "notes": "Quarterly checkup"
        }
    ]
    
    for apt in appointments:
        db.appointments.insert_one(apt)
        print(f"  ✓ Created appointment: {apt['patient_name']} on {apt['date']}")

def create_sample_prescriptions():
    """Create sample prescriptions"""
    print("\nCreating sample prescriptions...")
    
    db = Database.get_db()
    
    prescriptions = [
        {
            "patient_id": "P001",
            "patient_name": "John Smith",
            "doctor_id": "doctor1",
            "medication": "Lisinopril",
            "dosage": "10mg",
            "frequency": "Once daily",
            "duration": "30 days",
            "prescribed_date": datetime.now().isoformat(),
            "notes": "For blood pressure control"
        },
        {
            "patient_id": "P001",
            "patient_name": "John Smith",
            "doctor_id": "doctor1",
            "medication": "Metformin",
            "dosage": "500mg",
            "frequency": "Twice daily",
            "duration": "30 days",
            "prescribed_date": datetime.now().isoformat(),
            "notes": "For diabetes management"
        },
        {
            "patient_id": "P003",
            "patient_name": "Robert Williams",
            "doctor_id": "doctor1",
            "medication": "Furosemide",
            "dosage": "40mg",
            "frequency": "Once daily",
            "duration": "30 days",
            "prescribed_date": datetime.now().isoformat(),
            "notes": "Diuretic for fluid management"
        },
        {
            "patient_id": "P005",
            "patient_name": "Michael Brown",
            "doctor_id": "doctor1",
            "medication": "Epoetin Alfa",
            "dosage": "4000 units",
            "frequency": "Three times weekly",
            "duration": "Ongoing",
            "prescribed_date": datetime.now().isoformat(),
            "notes": "For anemia management in Stage 5 CKD"
        }
    ]
    
    for rx in prescriptions:
        db.prescriptions.insert_one(rx)
        print(f"  ✓ Created prescription: {rx['medication']} for {rx['patient_name']}")

def create_sample_lab_results():
    """Create sample lab results"""
    print("\nCreating sample lab results...")
    
    db = Database.get_db()
    
    lab_results = [
        {
            "patient_id": "P001",
            "patient_name": "John Smith",
            "test_date": (datetime.now() - timedelta(days=7)).isoformat(),
            "test_type": "Comprehensive Metabolic Panel",
            "results": {
                "eGFR": 45.2,
                "Creatinine": 2.1,
                "BUN": 28,
                "Albumin": 3.2,
                "Hemoglobin": 11.5,
                "Potassium": 4.8,
                "Sodium": 138
            },
            "doctor_id": "doctor1",
            "notes": "eGFR stable, continue current treatment"
        },
        {
            "patient_id": "P003",
            "patient_name": "Robert Williams",
            "test_date": (datetime.now() - timedelta(days=3)).isoformat(),
            "test_type": "Kidney Function Panel",
            "results": {
                "eGFR": 22.3,
                "Creatinine": 3.5,
                "BUN": 45,
                "Albumin": 2.8,
                "Hemoglobin": 9.8,
                "Potassium": 5.2,
                "Sodium": 135
            },
            "doctor_id": "doctor1",
            "notes": "Declining kidney function, consider dialysis consultation"
        }
    ]
    
    for lab in lab_results:
        db.lab_results.insert_one(lab)
        print(f"  ✓ Created lab result: {lab['test_type']} for {lab['patient_name']}")

def create_sample_education():
    """Create sample education resources"""
    print("\nCreating sample education resources...")
    
    db = Database.get_db()
    
    # Clear existing education resources
    db.education.delete_many({})
    
    education_resources = [
        {
            "title": "Understanding CKD Stages",
            "category": "General",
            "content": "Chronic Kidney Disease is divided into 5 stages based on eGFR levels...",
            "created_date": datetime.now().isoformat(),
            "author": "Dr. Smith"
        },
        {
            "title": "Diet and Nutrition for CKD",
            "category": "Nutrition",
            "content": "Proper diet is crucial for managing CKD. Key considerations include...",
            "created_date": datetime.now().isoformat(),
            "author": "Dr. Smith"
        },
        {
            "title": "Managing Blood Pressure with CKD",
            "category": "Treatment",
            "content": "Blood pressure control is essential for slowing CKD progression...",
            "created_date": datetime.now().isoformat(),
            "author": "Dr. Smith"
        }
    ]
    
    for edu in education_resources:
        db.education.insert_one(edu)
        print(f"  ✓ Created education resource: {edu['title']}")

def main():
    """Main initialization function"""
    print("=" * 60)
    print("CKD Diagnostic System - Database Initialization")
    print("=" * 60)
    
    try:
        # Initialize database connection
        Database.initialize()
        
        # Create collections and indexes
        init_collections()
        
        # Populate sample data
        create_sample_users()
        create_sample_patients_data()
        create_sample_appointments()
        create_sample_prescriptions()
        create_sample_lab_results()
        create_sample_education()
        
        print("\n" + "=" * 60)
        print("✓ Database initialization completed successfully!")
        print("=" * 60)
        
        # Print summary
        db = Database.get_db()
        print("\nDatabase Summary:")
        print(f"  - Users: {db.users.count_documents({})}")
        print(f"  - Patients Data: {db.patients_data.count_documents({})}")
        print(f"  - Appointments: {db.appointments.count_documents({})}")
        print(f"  - Prescriptions: {db.prescriptions.count_documents({})}")
        print(f"  - Lab Results: {db.lab_results.count_documents({})}")
        print(f"  - Education Resources: {db.education.count_documents({})}")
        
        print("\nSample Login Credentials:")
        print("  Doctor: username='doctor1', password='doctor123'")
        print("  Patient: username='john_smith', password='patient123'")
        
    except Exception as e:
        print(f"\n✗ Error during initialization: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
