"""
Test script for Langflow integration with prescription analysis
"""

import sys
import os
import json

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_prescription_analysis():
    """Test the prescription analysis functionality"""
    print("Testing prescription analysis functionality...")
    
    # Sample patient data
    patient_data = {
        'name': 'John Doe',
        'age': 65,
        'gender': 'Male',
        'ckd_stage': 'Stage 3b',
        'egfr': 45,
        'potassium': 4.2,
        'sodium': 138,
        'serum_creatinine': 1.8,
        'blood_urea': 40,
        'has_diabetes': True,
        'has_hypertension': True
    }
    
    # Sample prescription data
    prescription_data = {
        'medications': [
            {
                'name': 'Lisinopril',
                'dosage': '10mg',
                'frequency': 'Once daily',
                'notes': 'For blood pressure control'
            },
            {
                'name': 'Furosemide',
                'dosage': '40mg',
                'frequency': 'Once daily',
                'notes': 'Diuretic for fluid management'
            },
            {
                'name': 'Metformin',
                'dosage': '500mg',
                'frequency': 'Twice daily',
                'notes': 'For diabetes management'
            }
        ],
        'date': '2025-12-19',
        'doctor': 'Dr. Smith'
    }
    
    print("Patient data:", json.dumps(patient_data, indent=2))
    print("Prescription data:", json.dumps(prescription_data, indent=2))
    
    try:
        # Test AI recommender
        print("\n--- Testing AI Recommender ---")
        from models.ai_recommender import CKDAIRecommender
        recommender = CKDAIRecommender()
        
        # Test prescription analysis
        analysis_results = recommender.analyze_prescription(prescription_data, patient_data)
        print("AI Analysis Results:")
        print(json.dumps(analysis_results, indent=2))
        
        # Test PDF generation
        print("\n--- Testing PDF Generation ---")
        from models.prescription_report_generator import generate_prescription_report
        pdf_path = generate_prescription_report(patient_data, prescription_data, analysis_results)
        print(f"PDF Report generated at: {pdf_path}")
        
        print("\n✓ All tests passed!")
        return True
        
    except Exception as e:
        print(f"✗ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_prescription_analysis()