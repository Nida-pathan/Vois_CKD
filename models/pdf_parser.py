"""
PDF Lab Report Parser
Extracts medical values from lab report PDFs
"""

import PyPDF2
import re
from typing import Dict, Optional

class LabReportParser:
    """Parse lab reports and extract medical values"""
    
    # Common lab value patterns (case-insensitive regex)
    PATTERNS = {
        # Kidney function markers
        'serum_creatinine': r'(?:serum\s+)?creatinine[:\s]+(\d+\.?\d*)',
        'blood_urea': r'(?:blood\s+)?urea[:\s]+(\d+\.?\d*)',
        'egfr': r'egfr[:\s]+(\d+\.?\d*)',
        'bun': r'bun[:\s]+(\d+\.?\d*)',
        
        # Electrolytes
        'sodium': r'sodium[:\s]+(\d+\.?\d*)',
        'potassium': r'potassium[:\s]+(\d+\.?\d*)',
        'calcium': r'calcium[:\s]+(\d+\.?\d*)',
        'phosphorus': r'phosphorus[:\s]+(\d+\.?\d*)',
        
        # Blood counts
        'hemoglobin': r'(?:hb|hemoglobin)[:\s]+(\d+\.?\d*)',
        'hematocrit': r'hematocrit[:\s]+(\d+\.?\d*)',
        'wbc': r'(?:wbc|white\s+blood\s+cell)[:\s]+(\d+\.?\d*)',
        
        # Urine tests
        'urine_protein': r'(?:urine\s+)?protein[:\s]+(\d+\.?\d*)',
        'albumin': r'albumin[:\s]+(\d+\.?\d*)',
        
        # Other markers
        'uric_acid': r'uric\s+acid[:\s]+(\d+\.?\d*)',
        'glucose': r'glucose[:\s]+(\d+\.?\d*)',
    }
    
    def __init__(self, pdf_path: str):
        self.pdf_path = pdf_path
        self.text = self._extract_text()
    
    def _extract_text(self) -> str:
        """Extract text from PDF"""
        try:
            text = ""
            with open(self.pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page in pdf_reader.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text.lower() + "\n"
            return text
        except Exception as e:
            print(f"Error extracting PDF text: {e}")
            return ""
    
    def extract_values(self, disease_type: str = None) -> Dict[str, float]:
        """Extract relevant values based on disease type"""
        values = {}
        
        # Define relevant markers for each disease
        if disease_type == 'ckd':
            patterns = ['serum_creatinine', 'blood_urea', 'egfr', 'sodium', 'potassium', 
                       'hemoglobin', 'calcium', 'phosphorus']
        elif disease_type == 'kidney_stone':
            patterns = ['calcium', 'uric_acid', 'phosphorus', 'sodium', 'urine_protein']
        elif disease_type == 'aki':
            patterns = ['serum_creatinine', 'blood_urea', 'egfr', 'potassium', 'sodium']
        elif disease_type == 'esrd':
            patterns = ['serum_creatinine', 'blood_urea', 'egfr', 'hemoglobin', 'calcium', 
                       'phosphorus', 'potassium']
        else:
            # Extract all available values
            patterns = list(self.PATTERNS.keys())
        
        # Extract values using regex
        for pattern_name in patterns:
            if pattern_name in self.PATTERNS:
                match = re.search(self.PATTERNS[pattern_name], self.text, re.IGNORECASE)
                if match:
                    try:
                        values[pattern_name] = float(match.group(1))
                    except ValueError:
                        continue
        
        return values
    
    def get_all_values(self) -> Dict[str, float]:
        """Extract all detectable values"""
        values = {}
        for name, pattern in self.PATTERNS.items():
            match = re.search(pattern, self.text, re.IGNORECASE)
            if match:
                try:
                    values[name] = float(match.group(1))
                except ValueError:
                    continue
        return values
    
    def set_default_values(self, disease_type: str) -> Dict[str, float]:
        """Return default lab values for testing"""
        defaults = {
            'ckd': {
                'serum_creatinine': 1.5,
                'blood_urea': 45,
                'egfr': 55,
                'sodium': 140,
                'potassium': 4.5,
                'hemoglobin': 11.5,
                'calcium': 9.0,
                'phosphorus': 4.5
            },
            'kidney_stone': {
                'calcium': 10.5,
                'uric_acid': 7.5,
                'phosphorus': 3.5,
                'sodium': 142,
                'urine_protein': 150
            },
            'aki': {
                'serum_creatinine': 3.0,
                'blood_urea': 80,
                'egfr': 25,
                'potassium': 5.5,
                'sodium': 135
            },
            'esrd': {
                'serum_creatinine': 8.0,
                'blood_urea': 120,
                'egfr': 10,
                'hemoglobin': 9.0,
                'calcium': 8.0,
                'phosphorus': 6.5,
                'potassium': 5.8
            }
        }
        
        return defaults.get(disease_type, {})
