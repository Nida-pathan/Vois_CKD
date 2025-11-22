"""
Multi-Disease Predictor for Kidney-Related Conditions
Rule-based severity detection for CKD, Kidney Stone, AKI, and ESRD
"""

from models.ckd_model import ckd_model

class KidneyDiseasePredictor:
    """Unified kidney disease prediction system"""
    
    @staticmethod
    def predict_ckd(lab_values: dict) -> dict:
        """
        Predict CKD stage and risk using existing model
        """
        try:
            # Use existing CKD model if we have necessary values
            if 'serum_creatinine' in lab_values and 'blood_urea' in lab_values:
                prediction = ckd_model.predict_risk(lab_values)
                return {
                    'disease': 'Chronic Kidney Disease (CKD)',
                    'stage': prediction.get('stage', 'Unknown'),
                    'risk_level': prediction.get('risk_level', 'Unknown'),
                    'risk_percentage': prediction.get('risk_percentage', 0),
                    'severity': KidneyDiseasePredictor._calculate_severity(prediction),
                    'lab_values': lab_values,
                    'recommendations': KidneyDiseasePredictor._get_ckd_recommendations(prediction)
                }
            else:
                # Fallback to eGFR-based classification
                egfr = lab_values.get('egfr', 60)
                return KidneyDiseasePredictor._classify_by_egfr(egfr, lab_values)
        except Exception as e:
            print(f"Error in CKD prediction: {e}")
            return KidneyDiseasePredictor._get_default_prediction('CKD', lab_values)
    
    @staticmethod
    def predict_kidney_stone(lab_values: dict) -> dict:
        """
        Predict kidney stone risk based on lab values
        """
        risk_score = 0
        risk_factors = []
        
        # Calcium levels
        calcium = lab_values.get('calcium', 9.5)
        if calcium > 10.5:
            risk_score += 3
            risk_factors.append(f"High calcium ({calcium} mg/dL)")
        elif calcium > 10.0:
            risk_score += 1
            risk_factors.append(f"Elevated calcium ({calcium} mg/dL)")
        
        # Uric acid levels
        uric_acid = lab_values.get('uric_acid', 5.0)
        if uric_acid > 7.0:
            risk_score += 3
            risk_factors.append(f"High uric acid ({uric_acid} mg/dL)")
        elif uric_acid > 6.0:
            risk_score += 1
            risk_factors.append(f"Elevated uric acid ({uric_acid} mg/dL)")
        
        # Urine protein
        urine_protein = lab_values.get('urine_protein', 0)
        if urine_protein > 150:
            risk_score += 2
            risk_factors.append(f"Proteinuria ({urine_protein} mg/dL)")
        
        # Determine severity
        if risk_score >= 5:
            severity = 'High'
            stage = 'High Risk'
        elif risk_score >= 3:
            severity = 'Moderate'
            stage = 'Moderate Risk'
        else:
            severity = 'Low'
            stage = 'Low Risk'
        
        return {
            'disease': 'Kidney Stone',
            'stage': stage,
            'severity': severity,
            'risk_score': risk_score,
            'risk_factors': risk_factors if risk_factors else ['No significant risk factors detected'],
            'lab_values': lab_values,
            'recommendations': KidneyDiseasePredictor._get_stone_recommendations(severity)
        }
    
    @staticmethod
    def predict_aki(lab_values: dict) -> dict:
        """
        Predict Acute Kidney Injury (AKI) severity
        Based on KDIGO criteria
        """
        creatinine = lab_values.get('serum_creatinine', 1.0)
        egfr = lab_values.get('egfr', 90)
        
        # AKI staging based on creatinine increase
        if creatinine >= 4.0:
            stage = 'Stage 3 (Severe)'
            severity = 'High'
        elif creatinine >= 2.0:
            stage = 'Stage 2 (Moderate)'
            severity = 'Moderate'
        elif creatinine >= 1.5:
            stage = 'Stage 1 (Mild)'
            severity = 'Moderate'
        else:
            stage = 'No AKI'
            severity = 'Low'
        
        # Additional risk factors
        risk_factors = []
        potassium = lab_values.get('potassium', 4.0)
        if potassium > 5.5:
            risk_factors.append(f"Hyperkalemia ({potassium} mEq/L)")
        
        sodium = lab_values.get('sodium', 140)
        if sodium < 135:
            risk_factors.append(f"Hyponatremia ({sodium} mEq/L)")
        
        return {
            'disease': 'Acute Kidney Injury (AKI)',
            'stage': stage,
            'severity': severity,
            'creatinine': creatinine,
            'egfr': egfr,
            'risk_factors': risk_factors if risk_factors else ['Monitor kidney function closely'],
            'lab_values': lab_values,
            'recommendations': KidneyDiseasePredictor._get_aki_recommendations(stage)
        }
    
    @staticmethod
    def predict_esrd(lab_values: dict) -> dict:
        """
        Predict End-Stage Renal Disease (ESRD) status
        """
        egfr = lab_values.get('egfr', 60)
        creatinine = lab_values.get('serum_creatinine', 1.0)
        
        # ESRD classification
        if egfr < 15:
            stage = 'ESRD (Stage 5)'
            severity = 'Critical'
            dialysis_needed = True
        elif egfr < 30:
            stage = 'Severe CKD (Stage 4)'
            severity = 'High'
            dialysis_needed = False
        elif egfr < 60:
            stage = 'Moderate CKD (Stage 3)'
            severity = 'Moderate'
            dialysis_needed = False
        else:
            stage = 'Early CKD or Normal'
            severity = 'Low'
            dialysis_needed = False
        
        # Complications
        complications = []
        hemoglobin = lab_values.get('hemoglobin', 12.0)
        if hemoglobin < 10.0:
            complications.append(f"Anemia (Hb: {hemoglobin} g/dL)")
        
        calcium = lab_values.get('calcium', 9.0)
        phosphorus = lab_values.get('phosphorus', 3.5)
        if calcium < 8.5:
            complications.append(f"Hypocalcemia ({calcium} mg/dL)")
        if phosphorus > 5.5:
            complications.append(f"Hyperphosphatemia ({phosphorus} mg/dL)")
        
        potassium = lab_values.get('potassium', 4.0)
        if potassium > 5.5:
            complications.append(f"Hyperkalemia ({potassium} mEq/L)")
        
        return {
            'disease': 'End-Stage Renal Disease (ESRD)',
            'stage': stage,
            'severity': severity,
            'egfr': egfr,
            'creatinine': creatinine,
            'dialysis_needed': dialysis_needed,
            'complications': complications if complications else ['No major complications detected'],
            'lab_values': lab_values,
            'recommendations': KidneyDiseasePredictor._get_esrd_recommendations(severity, dialysis_needed)
        }
    
    # Helper methods
    @staticmethod
    def _calculate_severity(prediction: dict) -> str:
        """Calculate overall severity from CKD prediction"""
        risk_level = prediction.get('risk_level', 'Unknown')
        if risk_level in ['High', 'Very High']:
            return 'High'
        elif risk_level == 'Moderate':
            return 'Moderate'
        else:
            return 'Low'
    
    @staticmethod
    def _classify_by_egfr(egfr: float, lab_values: dict) -> dict:
        """Classify CKD by eGFR when model unavailable"""
        if egfr >= 90:
            stage = 'Stage 1'
            severity = 'Low'
        elif egfr >= 60:
            stage = 'Stage 2'
            severity = 'Low'
        elif egfr >= 45:
            stage = 'Stage 3a'
            severity = 'Moderate'
        elif egfr >= 30:
            stage = 'Stage 3b'
            severity = 'Moderate'
        elif egfr >= 15:
            stage = 'Stage 4'
            severity = 'High'
        else:
            stage = 'Stage 5'
            severity = 'Critical'
        
        return {
            'disease': 'Chronic Kidney Disease (CKD)',
            'stage': stage,
            'severity': severity,
            'egfr': egfr,
            'risk_level': severity,
            'lab_values': lab_values,
            'recommendations': KidneyDiseasePredictor._get_ckd_recommendations({'risk_level': severity})
        }
    
    @staticmethod
    def _get_default_prediction(disease: str, lab_values: dict) -> dict:
        """Return default prediction when analysis fails"""
        return {
            'disease': disease,
            'stage': 'Unknown',
            'severity': 'Unknown',
            'lab_values': lab_values,
            'recommendations': ['Please consult with your healthcare provider for detailed analysis.']
        }
    
    # Recommendation generators
    @staticmethod
    def _get_ckd_recommendations(prediction: dict) -> list:
        """Get CKD-specific recommendations"""
        risk = prediction.get('risk_level', 'Low')
        if risk in ['High', 'Critical']:
            return [
                'Consult a nephrologist immediately',
                'Follow strict low-sodium, low-potassium diet',
                'Monitor blood pressure daily',
                'Limit protein intake as advised',
                'Regular kidney function monitoring'
            ]
        elif risk == 'Moderate':
            return [
                'Schedule regular nephrology check-ups',
                'Maintain CKD-friendly diet',
                'Control blood pressure and blood sugar',
                'Stay hydrated (as per doctor\'s advice)',
                'Avoid nephrotoxic medications'
            ]
        else:
            return [
                'Maintain healthy lifestyle',
                'Regular health check-ups',
                'Stay hydrated',
                'Balanced diet and exercise'
            ]
    
    @staticmethod
    def _get_stone_recommendations(severity: str) -> list:
        """Get kidney stone recommendations"""
        if severity == 'High':
            return [
                'Consult urologist immediately',
                'Increase water intake (2-3 liters/day)',
                'Reduce sodium intake',
                'Limit foods high in oxalate',
                'Consider medication for stone prevention'
            ]
        elif severity == 'Moderate':
            return [
                'Increase fluid intake',
                'Reduce salt and animal protein',
                'Monitor calcium intake',
                'Regular urine tests',
                'Consult doctor about prevention'
            ]
        else:
            return [
                'Maintain adequate hydration',
                'Balanced diet',
                'Regular check-ups'
            ]
    
    @staticmethod
    def _get_aki_recommendations(stage: str) -> list:
        """Get AKI recommendations"""
        if 'Stage 3' in stage or 'Stage 2' in stage:
            return [
                'URGENT: Seek immediate medical attention',
                'May require hospitalization',
                'Possible dialysis needed',
                'Identify and treat underlying cause',
                'Monitor fluid and electrolyte balance'
            ]
        elif 'Stage 1' in stage:
            return [
                'Consult nephrologist promptly',
                'Monitor kidney function closely',
                'Identify underlying cause',
                'Adjust medications as needed',
                'Maintain proper hydration'
            ]
        else:
            return [
                'Continue monitoring kidney function',
                'Maintain healthy lifestyle',
                'Stay hydrated'
            ]
    
    @staticmethod
    def _get_esrd_recommendations(severity: str, dialysis_needed: bool) -> list:
        """Get ESRD recommendations"""
        if dialysis_needed:
            return [
                'CRITICAL: Immediate nephrology consultation required',
                'Dialysis preparation or initiation needed',
                'Consider kidney transplant evaluation',
                'Strict dietary restrictions',
                'Close monitoring of all lab values',
                'Manage complications (anemia, bone disease)'
            ]
        elif severity == 'High':
            return [
                'Regular nephrology follow-up essential',
                'Prepare for possible dialysis',
                'Strict CKD diet adherence',
                'Manage blood pressure and diabetes',
                'Monitor for complications',
                'Discuss treatment options with nephrologist'
            ]
        else:
            return [
                'Regular nephrology monitoring',
                'CKD-friendly lifestyle',
                'Control underlying conditions',
                'Medication adherence'
            ]
