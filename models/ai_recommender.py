"""
AI-Powered CKD Lifestyle Recommendation Engine
Uses Google Gemini API with HIPAA-compliant data handling
"""

import google.generativeai as genai
import os
import json
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class CKDAIRecommender:
    def __init__(self):
        """Initialize Gemini API"""
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key or api_key == 'your_gemini_api_key_here':
            raise ValueError("GEMINI_API_KEY not configured in .env file")
        
        genai.configure(api_key=api_key)
        
        # Use Gemini 2.5 Flash (verified available with this API key)
        self.model = genai.GenerativeModel('models/gemini-2.5-flash')
    
    def anonymize_patient_data(self, patient_data):
        """
        Remove all PII for HIPAA compliance
        Only clinical data is sent to API
        """
        age = patient_data.get('age', 50)
        
        # Determine age range (not exact age)
        if age < 30:
            age_range = 'under 30'
        elif age < 50:
            age_range = '30-50'
        elif age < 65:
            age_range = '50-65'
        else:
            age_range = 'over 65'
        
        return {
            'ckd_stage': patient_data.get('stage', 'N/A'),
            'egfr': patient_data.get('egfr', 60),
            'sodium': patient_data.get('sodium', 140),
            'potassium': patient_data.get('potassium', 4.0),
            'serum_creatinine': patient_data.get('serum_creatinine', 1.2),
            'blood_urea': patient_data.get('blood_urea', 20),
            'has_diabetes': patient_data.get('diabetes', False),
            'has_hypertension': patient_data.get('hypertension', False),
            'age_range': age_range,
            'smoking_status': patient_data.get('smoking_status', 'non-smoker'),
            'exercise_frequency': patient_data.get('exercise_frequency', 'rarely')
        }
    
    def generate_comprehensive_plan(self, patient_data):
        """
        Generate complete CKD lifestyle plan
        Returns: dict with all recommendations
        """
        anonymized_data = self.anonymize_patient_data(patient_data)
        
        prompt = f"""You are a helpful AI assistant providing educational information about kidney-friendly lifestyles. 
This is for informational purposes only and does not constitute medical advice.

Based on the following anonymized profile, suggest general lifestyle guidelines that are commonly recommended for similar profiles.

Profile:
- CKD Stage: {anonymized_data['ckd_stage']}
- eGFR: {anonymized_data['egfr']}
- Potassium: {anonymized_data['potassium']}
- Sodium: {anonymized_data['sodium']}
- Condition: {anonymized_data['has_diabetes']} (Diabetes), {anonymized_data['has_hypertension']} (Hypertension)

Provide a structured response in the following JSON format:

{{
  "diet_plan": {{
    "daily_sodium_limit_mg": 2000,
    "daily_potassium_limit_mg": 2000,
    "daily_protein_g": 60,
    "daily_fluid_limit_ml": 1500,
    "foods_to_avoid": ["list of 5 foods"],
    "recommended_foods": ["list of 5 foods"],
    "meal_timing": "general tip",
    "portion_guidelines": "general tip"
  }},
  "food_swaps": [
    {{
      "high_item": "High sodium/potassium food",
      "low_alternative": "Better alternative",
      "reason": "Why it helps",
      "sodium_saved_mg": 500,
      "potassium_saved_mg": 300
    }}
    // Include 5 swaps
  ],
  "hydration_plan": {{
    "daily_limit_liters": 1.5,
    "timing_tips": ["tip 1", "tip 2"],
    "warning_signs": ["sign 1", "sign 2"],
    "tracking_method": "method"
  }},
  "weekly_recipes": [
    {{
      "day": "Monday",
      "recipe_name": "Recipe Name",
      "meal_type": "Lunch",
      "ingredients": ["ing 1", "ing 2"],
      "instructions": ["step 1", "step 2"],
      "prep_time_minutes": 20,
      "nutrition_per_serving": {{
        "sodium_mg": 200,
        "potassium_mg": 150,
        "protein_g": 15,
        "calories": 300
      }}
    }}
    // Include 7 recipes
  ],
  "exercise_plan": {{
    "intensity_level": "moderate",
    "weekly_routine": [
      {{
        "day": "Monday",
        "activity": "Walking",
        "duration_minutes": 30,
        "intensity": "moderate",
        "precautions": "safety tip"
      }}
      // Include 7 days
    ],
    "general_precautions": ["precaution 1", "precaution 2"],
    "when_to_stop": ["warning sign 1", "warning sign 2"]
  }},
  "daily_routine": {{
    "morning": ["activity 1", "activity 2"],
    "afternoon": ["activity 1", "activity 2"],
    "evening": ["activity 1", "activity 2"],
    "sleep_schedule": "timing",
    "medication_reminders": ["reminder 1"]
  }}
}}

IMPORTANT: 
- Respond ONLY with valid JSON
- Do not include markdown formatting
- Keep suggestions general and educational"""

        try:
            # Configure generation options
            generation_config = genai.types.GenerationConfig(
                temperature=0.7,
                top_p=0.8,
                top_k=40,
                max_output_tokens=8192,
            )
            
            # Configure safety settings to avoid blocking
            # Using BLOCK_NONE to ensure educational content isn't flagged
            safety_settings = [
                {
                    "category": "HARM_CATEGORY_HARASSMENT",
                    "threshold": "BLOCK_NONE"
                },
                {
                    "category": "HARM_CATEGORY_HATE_SPEECH",
                    "threshold": "BLOCK_NONE"
                },
                {
                    "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                    "threshold": "BLOCK_NONE"
                },
                {
                    "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                    "threshold": "BLOCK_NONE"
                },
            ]
            
            response = self.model.generate_content(
                prompt,
                generation_config=generation_config,
                safety_settings=safety_settings
            )
            
            # Check if response was blocked
            if not response.parts:
                print(f"AI Response blocked. Feedback: {response.prompt_feedback}")
                return self._get_default_recommendations()
                
            return self._parse_response(response.text)
        except Exception as e:
            print(f"Error generating recommendations: {e}")
            # Log the full error for debugging
            import traceback
            traceback.print_exc()
            return self._get_default_recommendations()
    
    def _parse_response(self, response_text):
        """Parse Gemini response and extract JSON"""
        try:
            # Clean up the response text
            text = response_text.strip()
            
            # Remove markdown code blocks if present
            if '```json' in text:
                text = text.split('```json')[1]
                if '```' in text:
                    text = text.split('```')[0]
            elif '```' in text:
                text = text.split('```')[1]
                if '```' in text:
                    text = text.split('```')[0]
            
            # Additional cleanup for common issues
            text = text.strip()
            
            # Parse JSON
            recommendations = json.loads(text)
            print(f"Generated recommendations: {json.dumps(recommendations, indent=2)}")
            return recommendations
        except json.JSONDecodeError as e:
            print(f"JSON parsing error: {e}")
            print(f"Raw response: {response_text}")
            return self._get_default_recommendations()
    
    def _get_default_recommendations(self):
        """Fallback recommendations if AI fails"""
        return {
            "diet_plan": {
                "daily_sodium_limit_mg": 2000,
                "daily_potassium_limit_mg": 2000,
                "daily_protein_g": 60,
                "daily_fluid_limit_ml": 1500,
                "foods_to_avoid": [
                    "Processed meats", "Canned soups", "Fast food",
                    "Bananas", "Oranges", "Tomatoes",
                    "Potatoes", "Dairy products", "Nuts", "Chocolate"
                ],
                "recommended_foods": [
                    "Fresh chicken", "Fish", "Eggs",
                    "Apples", "Berries", "Grapes",
                    "Cauliflower", "Cabbage", "Cucumber", "Rice"
                ],
                "meal_timing": "Eat 3 balanced meals with 2 small snacks",
                "portion_guidelines": "Use your palm for protein, fist for carbs"
            },
            "food_swaps": [
                {
                    "high_item": "Regular salt",
                    "low_alternative": "Herbs and spices",
                    "reason": "Reduces sodium intake",
                    "sodium_saved_mg": 2000,
                    "potassium_saved_mg": 0
                }
            ],
            "hydration_plan": {
                "daily_limit_liters": 1.5,
                "timing_tips": [
                    "Spread fluid intake throughout the day",
                    "Limit fluids 2 hours before bed",
                    "Track intake with a water bottle"
                ],
                "warning_signs": [
                    "Swelling in legs or ankles",
                    "Shortness of breath",
                    "Rapid weight gain"
                ],
                "tracking_method": "Use a marked water bottle"
            },
            "weekly_recipes": [],
            "exercise_plan": {
                "intensity_level": "moderate",
                "weekly_routine": [],
                "general_precautions": [
                    "Stay hydrated",
                    "Stop if you feel dizzy",
                    "Consult doctor before starting"
                ],
                "when_to_stop": [
                    "Chest pain",
                    "Severe shortness of breath",
                    "Dizziness or nausea"
                ]
            },
            "daily_routine": {
                "morning": ["Take medications", "Light breakfast", "Morning walk"],
                "afternoon": ["Balanced lunch", "Rest period", "Light activity"],
                "evening": ["Healthy dinner", "Relaxation", "Prepare for bed"],
                "sleep_schedule": "Aim for 7-8 hours, sleep by 10 PM",
                "medication_reminders": ["Take with food", "Set phone alarms"]
            }
        }


# Helper function for easy import
def get_ai_recommender():
    """Factory function to create AI recommender instance"""
    return CKDAIRecommender()
