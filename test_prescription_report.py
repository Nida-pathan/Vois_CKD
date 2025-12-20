"""
Test script to verify prescription report generation functionality
"""

import sys
import os

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_prescription_report_generation():
    """Test the prescription report generation functionality"""
    print("Testing prescription report generation...")
    
    try:
        # Get prescription from database
        from models.database import Database
        from models.user import get_prescription_by_id, get_patient_records
        
        db = Database.get_db()
        prescription = db.prescriptions.find_one()
        
        if not prescription:
            print("No prescriptions found in database")
            return False
            
        prescription_id = str(prescription['_id'])
        print(f"Found prescription with ID: {prescription_id}")
        
        # Test getting prescription by ID
        fetched_prescription = get_prescription_by_id(prescription_id)
        if not fetched_prescription:
            print("Failed to fetch prescription by ID")
            return False
            
        print("Successfully fetched prescription by ID")
        
        # Get patient data
        patient_username = fetched_prescription.get('patient')
        if not patient_username:
            print("No patient information in prescription")
            return False
            
        patient_data = get_patient_records(patient_username)
        if not patient_data:
            print("Failed to fetch patient data")
            return False
            
        print("Successfully fetched patient data")
        
        # Test AI analysis
        from models.ai_recommender import CKDAIRecommender
        recommender = CKDAIRecommender()
        
        # For testing purposes, let's add some mock patient data if it doesn't exist
        if 'egfr' not in patient_data:
            patient_data.update({
                'egfr': 45,
                'potassium': 4.2,
                'sodium': 138,
                'serum_creatinine': 1.8,
                'blood_urea': 40,
                'has_diabetes': False,
                'has_hypertension': True,
                'stage': 'Stage 3b'
            })
        
        analysis_results = recommender.analyze_prescription(fetched_prescription, patient_data)
        print("AI analysis completed successfully")
        print(f"Analysis results keys: {list(analysis_results.keys())}")
        
        # Test PDF generation
        from models.prescription_report_generator import generate_prescription_report
        pdf_path = generate_prescription_report(patient_data, fetched_prescription, analysis_results)
        print(f"PDF report generated successfully at: {pdf_path}")
        
        print("\n✅ All tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_prescription_report_generation()