"""
Demonstration script for the Langflow Prescription Analysis Agent
Shows how to use the implemented Langflow integration
"""

import sys
import os
import json
import requests

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def demonstrate_langflow_integration():
    """Demonstrate the Langflow prescription analysis agent"""
    print("=" * 60)
    print("LANGFLOW PRESCRIPTION ANALYSIS AGENT DEMONSTRATION")
    print("=" * 60)
    
    print("\nThis demonstration shows how to use the Langflow integration")
    print("for prescription analysis in the CKD diagnostic system.")
    
    # Sample patient data
    patient_data = {
        'name': 'Jane Smith',
        'age': 72,
        'gender': 'Female',
        'ckd_stage': 'Stage 3b',
        'egfr': 42,
        'potassium': 4.8,
        'sodium': 135,
        'serum_creatinine': 2.1,
        'blood_urea': 45,
        'has_diabetes': False,
        'has_hypertension': True
    }
    
    # Sample prescription data
    prescription_data = {
        'medications': [
            {
                'name': 'Losartan',
                'dosage': '50mg',
                'frequency': 'Once daily',
                'notes': 'For blood pressure control'
            },
            {
                'name': 'Spironolactone',
                'dosage': '25mg',
                'frequency': 'Once daily',
                'notes': 'Potassium-sparing diuretic'
            },
            {
                'name': 'Atorvastatin',
                'dosage': '20mg',
                'frequency': 'Once daily',
                'notes': 'For cholesterol management'
            }
        ],
        'date': '2025-12-19',
        'doctor': 'Dr. Johnson'
    }
    
    print("\nSample Input Data:")
    print("-" * 30)
    print("Patient Data:")
    print(json.dumps(patient_data, indent=2))
    print("\nPrescription Data:")
    print(json.dumps(prescription_data, indent=2))
    
    # In a real implementation with Langflow, you would:
    # 1. Send this data to the Langflow workflow
    # 2. The workflow would process it through the components we created
    # 3. Return the analysis results and PDF report
    
    print("\n" + "=" * 60)
    print("HOW TO USE WITH LANGFLOW:")
    print("=" * 60)
    
    print("""
1. START LANGFLOW SERVER:
   Run the following command in your terminal:
   langflow run

2. ACCESS THE INTERFACE:
   Open your browser and go to: http://localhost:7860

3. LOAD THE WORKFLOW:
   - Create a new flow
   - Import the workflow from: langflow_workflows/prescription_analysis.json
   - Or manually recreate the components as described in the JSON file

4. RUN THE ANALYSIS:
   - Input the patient and prescription data
   - The workflow will:
     * Process the data through our Python components
     * Analyze the prescription using the AI recommender
     * Generate a PDF report
     * Return the report for download

5. INTEGRATION WITH YOUR FLASK APP:
   The API endpoints we created allow seamless integration:
   - POST /langflow/prescription-analysis
   - POST /langflow/generate-report
   
   These endpoints handle the processing and PDF generation.
    """)
    
    print("\n" + "=" * 60)
    print("TECHNOLOGIES USED:")
    print("=" * 60)
    print("""
- Langflow: Visual workflow builder and execution engine
- Python: Backend processing and AI integration
- Flask: Web framework for API endpoints
- Google Gemini API: AI analysis of prescriptions
- fpdf: PDF generation library
- MongoDB: Data storage (existing infrastructure)
    """)
    
    print("\n" + "=" * 60)
    print("WORKFLOW COMPONENTS:")
    print("=" * 60)
    print("""
1. CHAT INPUT:
   - Receives prescription details from user/doctor

2. DATA PROCESSOR:
   - Parses and structures the input data
   - Prepares data for AI analysis

3. AI ANALYZER:
   - Uses our existing CKDAIRecommender
   - Analyzes prescription in context of CKD
   - Provides clinical insights and recommendations

4. PDF GENERATOR:
   - Creates professional medical reports
   - Uses our prescription_report_generator module

5. FILE OUTPUT:
   - Delivers the generated PDF to the user
    """)
    
    print("\n" + "=" * 60)
    print("BENEFITS OF THIS APPROACH:")
    print("=" * 60)
    print("""
✓ Visual workflow design and management
✓ Modular, reusable components
✓ Easy to modify and extend
✓ Seamless integration with existing system
✓ Professional PDF reports for medical use
✓ AI-powered clinical insights
✓ HIPAA-compliant data handling
    """)
    
    print("\nDemonstration complete!")

if __name__ == "__main__":
    demonstrate_langflow_integration()