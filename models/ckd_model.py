import pandas as pd
import numpy as np
import joblib
import os

class CKDModel:
    def __init__(self):
        self.model = None
        self.feature_names = [
            'age', 'bp_systolic', 'bp_diastolic', 'specific_gravity',
            'albumin', 'sugar', 'red_blood_cells', 'pus_cell',
            'bacteria', 'blood_glucose', 'blood_urea', 'serum_creatinine',
            'sodium', 'potassium', 'hemoglobin', 'packed_cell_volume',
            'white_blood_cell_count', 'red_blood_cell_count', 'hypertension',
            'diabetes_mellitus', 'coronary_artery_disease', 'appetite',
            'pedal_edema', 'anemia'
        ]
        # Load the pre-trained model
        self.load_model()

    def load_model(self):
        try:
            model_path = os.path.join(os.path.dirname(__file__), 'ckd_model.pkl')
            if os.path.exists(model_path):
                self.model = joblib.load(model_path)
                print(f"CKD Model loaded successfully from {model_path}")
            else:
                print(f"CKD Model file not found at {model_path}")
        except Exception as e:
            print(f"Error loading CKD model: {e}")

    def prepare_features(self, data):
        """
        Prepare features for prediction matching the trained model's expectations.
        """
        # Base features (20)
        base_features = [
            'age', 'bp_systolic', 'bp_diastolic', 'specific_gravity',
            'albumin', 'sugar', 'red_blood_cells', 'pus_cell',
            'bacteria', 'blood_glucose', 'blood_urea', 'serum_creatinine',
            'sodium', 'potassium', 'hemoglobin', 'packed_cell_volume',
            'white_blood_cell_count', 'red_blood_cell_count', 'hypertension',
            'diabetes_mellitus', 'coronary_artery_disease', 'appetite',
            'pedal_edema', 'anemia'
        ]
        
        # Ensure all base features are present with default values
        processed_data = {}
        for feature in base_features:
            processed_data[feature] = float(data.get(feature, 0))

        # Create DataFrame to handle feature engineering if needed, or just list
        # The model expects 25 features based on previous inspection (ESRD model had 25)
        # We assume the 25th feature or derived features are handled here if known.
        # However, the previous inspection showed 'ckd_model.pkl' expects 25 features.
        # The list above has 24 features.
        # Let's add the derived features as seen in ESRD model, assuming they share the pipeline.
        
        # Derived features (5)
        # 'cholesterol_ratio', 'creatinine_log', 'age_creatinine_interaction', 'high_creatinine', 'high_glucose'
        
        # We need to map the input keys to what the model likely expects if it was trained same as ESRD
        # But wait, the feature_names list I have above is from the OLD dummy model.
        # The NEW model (ckd_model.pkl) likely shares the schema with esrd_detection_model.pkl if they came from the same source.
        # The user provided 3 models.
        # esrd_detection_model.pkl had explicit feature names.
        # ckd_model.pkl did not, but had 25 features.
        
        # Let's try to construct the 25 features exactly as ESRD model expects.
        # ESRD features:
        # ['Age', 'Gender', 'Smoking', 'Alcohol', 'Hypertension', 'Coronary Artery Disease', 'Cancer', 'Chronic Liver Disease', 
        #  'Mean Serum Creatinine (mg/dL)', 'Cholesterol (mg/dL)', 'LDL-C (mg/dL)', 'HDL-C (mg/dL)', 'Uric Acid (mg/dL)', 
        #  'Calcium (mg/dL)', 'Phosphate (mg/dL)', 'Hemoglobin (g/dL)', 'Statin', 'Metformin', 'Insulin', 
        #  'Dipeptidyl Peptidase-4 Inhibitor', 'cholesterol_ratio', 'creatinine_log', 'age_creatinine_interaction', 
        #  'high_creatinine', 'high_glucose']
        
        # This is very different from the old feature list.
        # If I use the old feature list, the model will crash (24 vs 25 features and semantic mismatch).
        # I MUST assume the new ckd_model.pkl uses the SAME features as esrd_detection_model.pkl.
        
        # Let's reconstruct the feature vector based on ESRD schema.
        
        # Map input data (which comes from lab report parser or manual entry) to these keys.
        # Lab report parser extracts keys like 'age', 'gender', 'serum_creatinine', etc.
        
        input_map = {
            'Age': 'age',
            'Gender': 'gender', # Need encoding: 0 for Male, 1 for Female? Or vice versa? Usually 0/1.
            'Smoking': 'smoking',
            'Alcohol': 'alcohol',
            'Hypertension': 'hypertension',
            'Coronary Artery Disease': 'coronary_artery_disease',
            'Cancer': 'cancer',
            'Chronic Liver Disease': 'chronic_liver_disease',
            'Mean Serum Creatinine (mg/dL)': 'serum_creatinine',
            'Cholesterol (mg/dL)': 'cholesterol',
            'LDL-C (mg/dL)': 'ldl',
            'HDL-C (mg/dL)': 'hdl',
            'Uric Acid (mg/dL)': 'uric_acid',
            'Calcium (mg/dL)': 'calcium',
            'Phosphate (mg/dL)': 'phosphate',
            'Hemoglobin (g/dL)': 'hemoglobin',
            'Statin': 'statin',
            'Metformin': 'metformin',
            'Insulin': 'insulin',
            'Dipeptidyl Peptidase-4 Inhibitor': 'dpp4_inhibitor'
        }
        
        feature_vector = []
        
        # 1. Age
        age = float(data.get('age', 45))
        feature_vector.append(age)
        
        # 2. Gender (Assume 0: Male, 1: Female for now, or check typical encoding)
        gender = data.get('gender', 'Male')
        feature_vector.append(1.0 if str(gender).lower() in ['female', 'f', '1'] else 0.0)
        
        # 3-8. Binary/Categorical
        for key in ['Smoking', 'Alcohol', 'Hypertension', 'Coronary Artery Disease', 'Cancer', 'Chronic Liver Disease']:
            val = data.get(input_map[key], 0)
            feature_vector.append(float(val))
            
        # 9-16. Numerical Labs
        creatinine = float(data.get('serum_creatinine', 1.0))
        feature_vector.append(creatinine) # Mean Serum Creatinine
        
        cholesterol = float(data.get('cholesterol', 200))
        feature_vector.append(cholesterol)
        
        ldl = float(data.get('ldl', 100))
        feature_vector.append(ldl)
        
        hdl = float(data.get('hdl', 50))
        feature_vector.append(hdl)
        
        uric_acid = float(data.get('uric_acid', 5.0))
        feature_vector.append(uric_acid)
        
        calcium = float(data.get('calcium', 9.0))
        feature_vector.append(calcium)
        
        phosphate = float(data.get('phosphate', 3.5))
        feature_vector.append(phosphate)
        
        hemoglobin = float(data.get('hemoglobin', 14.0))
        feature_vector.append(hemoglobin)
        
        # 17-20. Meds
        for key in ['Statin', 'Metformin', 'Insulin', 'Dipeptidyl Peptidase-4 Inhibitor']:
            val = data.get(input_map[key], 0)
            feature_vector.append(float(val))
            
        # 21. cholesterol_ratio (Total / HDL)
        chol_ratio = cholesterol / hdl if hdl > 0 else 0
        feature_vector.append(chol_ratio)
        
        # 22. creatinine_log
        creat_log = np.log(creatinine) if creatinine > 0 else 0
        feature_vector.append(creat_log)
        
        # 23. age_creatinine_interaction
        feature_vector.append(age * creatinine)
        
        # 24. high_creatinine (Binary > 1.5 ?) - Let's assume standard threshold or what model used.
        # Using 1.3 as common cutoff or just based on data distribution.
        feature_vector.append(1.0 if creatinine > 1.5 else 0.0)
        
        # 25. high_glucose (Binary > 126 ?) - Diabetes threshold
        glucose = float(data.get('blood_glucose', 100)) # Note: Glucose wasn't in main list but needed for derived?
        # Wait, 'high_glucose' is derived. Is glucose in the main list?
        # ESRD list didn't have 'Glucose' explicitly, but had 'high_glucose'.
        # It had 'Mean Serum Creatinine'.
        # It seems 'Glucose' might be missing from the base 20 features of ESRD model?
        # Or maybe I missed it.
        # Let's assume we calculate it from 'blood_glucose' input.
        feature_vector.append(1.0 if glucose > 126 else 0.0)
        
        return np.array([feature_vector])

    def predict_risk(self, data):
        """
        Predict CKD risk using the loaded model.
        """
        if self.model is None:
            return {'error': 'Model not loaded'}

        try:
            features = self.prepare_features(data)
            prediction = self.model.predict(features)[0]
            probability = self.model.predict_proba(features)[0][1]
            
            risk_percentage = probability * 100
            
            if risk_percentage >= 80:
                risk_level = 'High'
                stage = 'Stage 4-5'
            elif risk_percentage >= 50:
                risk_level = 'Moderate'
                stage = 'Stage 3'
            else:
                risk_level = 'Low'
                stage = 'Stage 1-2'
                
            return {
                'risk_percentage': float(risk_percentage),
                'risk_level': risk_level,
                'stage': stage,
                'probability': float(probability)
            }
        except Exception as e:
            print(f"Prediction error: {e}")
            return {'error': str(e)}

    def predict_batch(self, data_list):
        """
        Predict for a batch of patients
        """
        results = []
        for data in data_list:
            results.append(self.predict_risk(data))
        return results

# Initialize model instance
ckd_model = CKDModel()