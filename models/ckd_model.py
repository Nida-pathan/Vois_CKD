import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
import joblib
import os

class CKDModel:
    def __init__(self):
        self.model = None
        self.scaler = StandardScaler()
        self.feature_names = [
            'age', 'bp_systolic', 'bp_diastolic', 'specific_gravity',
            'albumin', 'sugar', 'red_blood_cells', 'pus_cell',
            'bacteria', 'blood_glucose', 'blood_urea', 'serum_creatinine',
            'sodium', 'potassium', 'hemoglobin', 'packed_cell_volume',
            'white_blood_cell_count', 'red_blood_cell_count', 'hypertension',
            'diabetes_mellitus', 'coronary_artery_disease', 'appetite',
            'pedal_edema', 'anemia'
        ]
        # Only train model if not running on Vercel (to save time during build)
        if not os.environ.get('VERCEL'):
            self.train_model()
    
    def train_model(self):
        np.random.seed(42)
        n_samples = 1000
        
        X_healthy = np.random.randn(n_samples // 2, len(self.feature_names))
        X_healthy[:, 0] = np.random.uniform(20, 60, n_samples // 2)
        X_healthy[:, 1] = np.random.uniform(110, 130, n_samples // 2)
        X_healthy[:, 2] = np.random.uniform(70, 85, n_samples // 2)
        X_healthy[:, 11] = np.random.uniform(0.5, 1.2, n_samples // 2)
        X_healthy[:, 10] = np.random.uniform(10, 40, n_samples // 2)
        X_healthy[:, 14] = np.random.uniform(12, 17, n_samples // 2)
        
        X_ckd = np.random.randn(n_samples // 2, len(self.feature_names))
        X_ckd[:, 0] = np.random.uniform(45, 80, n_samples // 2)
        X_ckd[:, 1] = np.random.uniform(140, 180, n_samples // 2)
        X_ckd[:, 2] = np.random.uniform(90, 120, n_samples // 2)
        X_ckd[:, 11] = np.random.uniform(1.5, 8.0, n_samples // 2)
        X_ckd[:, 10] = np.random.uniform(50, 150, n_samples // 2)
        X_ckd[:, 14] = np.random.uniform(6, 12, n_samples // 2)
        
        X = np.vstack([X_healthy, X_ckd])
        y = np.hstack([np.zeros(n_samples // 2), np.ones(n_samples // 2)])
        
        self.scaler.fit(X)
        X_scaled = self.scaler.transform(X)
        
        self.model = RandomForestClassifier(n_estimators=100, random_state=42, max_depth=10)
        self.model.fit(X_scaled, y)
    
    def predict_risk(self, patient_data):
        # If model hasn't been trained yet (e.g., on Vercel), train it now
        if self.model is None:
            self.train_model()
            
        features = self.prepare_features(patient_data)
        features_scaled = self.scaler.transform([features])
        
        risk_prob = self.model.predict_proba(features_scaled)[0][1]
        risk_percentage = int(risk_prob * 100)
        
        stage = self.calculate_ckd_stage(patient_data)
        
        feature_importance = self.get_feature_importance(features)
        
        return {
            'risk_percentage': risk_percentage,
            'stage': stage,
            'risk_level': self.get_risk_level(risk_percentage),
            'feature_importance': feature_importance,
            'egfr': self.calculate_egfr(patient_data.get('age'), patient_data.get('serum_creatinine', 1.0), patient_data.get('gender', 'male'))
        }
    
    def prepare_features(self, data):
        features = []
        for feature_name in self.feature_names:
            if feature_name in data:
                features.append(float(data[feature_name]))
            else:
                features.append(0.0)
        return features
    
    def calculate_egfr(self, age, creatinine, gender):
        if creatinine <= 0:
            creatinine = 1.0
        
        if gender.lower() == 'female':
            egfr = 186 * (creatinine ** -1.154) * (age ** -0.203) * 0.742
        else:
            egfr = 186 * (creatinine ** -1.154) * (age ** -0.203)
        
        return round(egfr, 2)
    
    def calculate_ckd_stage(self, data):
        egfr = self.calculate_egfr(
            data.get('age', 50),
            data.get('serum_creatinine', 1.0),
            data.get('gender', 'male')
        )
        
        if egfr >= 90:
            return 1
        elif egfr >= 60:
            return 2
        elif egfr >= 30:
            return 3
        elif egfr >= 15:
            return 4
        else:
            return 5
    
    def get_risk_level(self, risk_percentage):
        if risk_percentage < 20:
            return 'Low'
        elif risk_percentage < 50:
            return 'Moderate'
        elif risk_percentage < 75:
            return 'High'
        else:
            return 'Critical'
    
    def get_feature_importance(self, features):
        # If model hasn't been trained yet, return empty list
        if self.model is None:
            return []
            
        importance = self.model.feature_importances_
        feature_importance = []
        
        for i, (name, value, imp) in enumerate(zip(self.feature_names, features, importance)):
            if imp > 0.01:
                feature_importance.append({
                    'name': name.replace('_', ' ').title(),
                    'value': round(value, 2),
                    'importance': round(imp * 100, 2)
                })
        
        return sorted(feature_importance, key=lambda x: x['importance'], reverse=True)[:5]
    
    def predict_batch(self, patient_list):
        results = []
        for patient in patient_list:
            result = self.predict_risk(patient)
            result['patient_id'] = patient.get('patient_id', 'Unknown')
            result['patient_name'] = patient.get('patient_name', 'Unknown')
            results.append(result)
        return results

ckd_model = CKDModel()