"""
Patient Education Chatbot for CKD Diagnostic System
Provides 24/7 support for basic inquiries about CKD stages, symptoms, and medical terminology
"""

import os
import json
from datetime import datetime
from models.ai_recommender import CKDAIRecommender

class PatientEducationChatbot:
    def __init__(self):
        self.recommender = CKDAIRecommender()
        self.conversation_history = []
        
        # Initialize RAG Engine
        try:
            from models.rag_engine import get_rag_engine
            self.rag_engine = get_rag_engine()
            
            # Initial ingestion if needed (checking if collection is empty)
            # This is a simplified check; in prod you might want a more robust one
            # or an admin trigger for ingestion.
            # For this demo, we'll try to ingest if we can't find anything.
            if self.rag_engine.vector_store._collection.count() == 0:
                print("Retrieval database empty. Ingesting documents...")
                self.rag_engine.ingest_documents()
                
            self.rag_enabled = True
        except Exception as e:
            print(f"Failed to initialize RAG engine: {e}")
            self.rag_enabled = False
            self.knowledge_base = self._load_knowledge_base() # Fallback
    
    def _load_knowledge_base(self):
        """Load the knowledge base for common CKD questions (Fallback)"""
        return {
            "ckd_stages": {
                "stage_1": "Stage 1 CKD means you have mild kidney damage with normal or high kidney function (eGFR > 90). At this stage, you may not have any symptoms.",
                "stage_2": "Stage 2 CKD means you have mild kidney damage with a mild decrease in kidney function (eGFR 60-89). Like stage 1, you may not have symptoms.",
                "stage_3a": "Stage 3a CKD means you have moderate kidney damage with a moderate decrease in kidney function (eGFR 45-59). You may start to experience symptoms like fatigue, swelling, or changes in urination.",
                "stage_3b": "Stage 3b CKD means you have moderate kidney damage with a moderate decrease in kidney function (eGFR 30-44). Symptoms may become more noticeable at this stage.",
                "stage_4": "Stage 4 CKD means you have severe kidney damage with a severe decrease in kidney function (eGFR 15-29). Symptoms are usually more pronounced, and preparation for kidney replacement therapy may begin.",
                "stage_5": "Stage 5 CKD means you have kidney failure (eGFR < 15). At this stage, dialysis or a kidney transplant is needed to sustain life."
            },
            "common_symptoms": {
                "fatigue": "Feeling tired or weak is common in CKD because your kidneys aren't able to remove waste products effectively, and you may have anemia.",
                "swelling": "Swelling (edema) in your legs, ankles, or around your eyes happens because your kidneys can't remove extra fluid from your body.",
                "urination_changes": "Changes in urination (more or less frequent, foamy, or dark-colored) can occur because damaged kidneys affect how your body filters waste.",
                "nausea": "Nausea and loss of appetite can happen when waste products build up in your blood because your kidneys aren't filtering effectively.",
                "sleep_issues": "Sleep problems are common in CKD patients and may be related to restless leg syndrome, sleep apnea, or other factors."
            },
            "medical_terms": {
                "egfr": "eGFR (estimated Glomerular Filtration Rate) is a blood test that estimates how well your kidneys are filtering waste from your blood. It's calculated using your creatinine level, age, sex, and race.",
                "creatinine": "Creatinine is a waste product from muscle activity that healthy kidneys remove from your blood. Higher levels in your blood may indicate reduced kidney function.",
                "albumin": "Albumin is a protein that can leak into your urine when your kidneys are damaged. A urine albumin test helps diagnose and monitor kidney disease.",
                "potassium": "Potassium is a mineral that helps your nerves and muscles work properly. In CKD, potassium levels can become too high (hyperkalemia) because your kidneys can't remove excess potassium.",
                "phosphorus": "Phosphorus is a mineral that helps keep your bones healthy. In CKD, phosphorus levels can build up because your kidneys can't remove excess phosphorus, which can weaken bones.",
                "anemia": "Anemia is a condition where you don't have enough red blood cells. In CKD, the kidneys produce less erythropoietin (EPO), a hormone that stimulates red blood cell production.",
                "dialysis": "Dialysis is a treatment that filters and purifies the blood using a machine. It's needed when your kidneys can no longer do the job adequately (usually Stage 5 CKD).",
                "transplant": "A kidney transplant is a surgical procedure to place a healthy kidney from a donor into your body when your own kidneys have failed."
            },
            "lifestyle": {
                "diet": "A kidney-friendly diet limits protein, sodium, phosphorus, and potassium. Work with a dietitian to create a meal plan tailored to your stage of CKD.",
                "exercise": "Regular physical activity can help control blood pressure, maintain bone strength, and improve mood. Aim for at least 30 minutes of moderate exercise most days.",
                "hydration": "Drink adequate fluids unless your doctor tells you to restrict fluids. The right amount varies based on your stage of CKD and other health conditions.",
                "medications": "Take all medications as prescribed. Some over-the-counter medications like NSAIDs (ibuprofen, naproxen) can harm your kidneys. Always check with your doctor or pharmacist."
            }
        }
    
    def get_welcome_message(self, patient_name=None):
        """Generate a personalized welcome message for the patient"""
        name = patient_name if patient_name else "Patient"
        return f"Hello {name}! 👋 I'm your KidneyCompanion assistant, now powered by AI. I can answer your questions about CKD based on the latest medical guidelines and your specific health data. How can I help you today?"
    
    def process_message(self, message, patient_data=None):
        """Process a patient message and generate an appropriate response"""
        # Add message to conversation history
        self.conversation_history.append({
            "role": "patient",
            "message": message,
            "timestamp": datetime.now().isoformat()
        })
        
        # Generate response
        try:
            if self.rag_enabled:
                response = self._generate_rag_response(message, patient_data)
            else:
                # Fallback to rule-based if RAG is broken
                response = self._generate_fallback_response(message.lower(), patient_data)
        except Exception as e:
            print(f"Error generating response: {e}")
            response = "I apologize, but I'm having trouble retrieving information right now. Please try again later."
            
        # Add response to conversation history
        self.conversation_history.append({
            "role": "assistant",
            "message": response,
            "timestamp": datetime.now().isoformat()
        })
        
        return response
    
    def _generate_rag_response(self, message, patient_data=None):
        """Generate a response using RAG and Gemini"""
        
        # 1. Retrieve Context
        context = "No specific medical documents found."
        try:
            retrieved_docs = self.rag_engine.search(message, k=3)
            if retrieved_docs:
                context = "\n\n".join(retrieved_docs)
        except Exception as e:
            print(f"RAG Search failed: {e}")
            
        # 2. Format Patient Data
        patient_context = "Patient Data: Not available."
        if patient_data:
            # Anonymize/simplify for the prompt
            p = patient_data
            patient_context = f"""
            Patient Profile:
            - Age: {p.get('age', 'Unknown')}
            - CKD Stage: {p.get('stage', 'Unknown')}
            - eGFR: {p.get('egfr', 'Unknown')}
            - Creatinine: {p.get('serum_creatinine', 'Unknown')}
            - Potassium: {p.get('potassium', 'Unknown')}
            - Symptoms: {', '.join([k for k,v in p.get('symptoms', {}).items() if v]) or 'None reported'}
            """
            
        # 3. Construct Prompt
        prompt = f"""
You are KidneyCompanion, a helpful and empathetic medical assistant for CKD patients.
Use the following context and patient data to answer the user's question.

CONTEXT FROM KNOWLEDGE BASE:
{context}

{patient_context}

USER QUESTION:
{message}

INSTRUCTIONS:
1. Answer the question directly using the Context provided.
2. If the Patient Data is relevant (e.g., they ask about diet and their potassium is high), personalize the advice.
3. If the answer is not in the context, use your general medical knowledge but mention you are providing general advice.
4. Keep the tone supportive and easy to understand (grade 8 reading level).
5. Always advise consulting a doctor for specific medical decisions.
6. Keep the response concise (under 150 words).

ANSWER:
"""
        
        # 4. Generate with Gemini
        try:
            response = self.recommender.model.generate_content(prompt)
            return response.text
        except Exception as e:
            print(f"Gemini generation failed: {e}")
            return "I'm having trouble connecting to my AI brain right now. Please try again in a moment."

    def _generate_fallback_response(self, message, patient_data=None):
        """Generate a response based on keywords (Legacy/Fallback)"""
        # Check for greetings
        if any(greeting in message for greeting in ["hello", "hi", "hey", "good morning", "good afternoon", "good evening"]):
            return "Hello! How can I help you with your kidney health today?"
        
        # Check for CKD stage questions
        if "stage" in message:
            for stage_key, description in self.knowledge_base["ckd_stages"].items():
                if stage_key.replace("_", " ") in message or stage_key.replace("_", "") in message:
                    return description
            return "CKD has 5 stages based on your eGFR (kidney function):\n\n" + \
                   "\n".join([f"• {key.replace('_', ' ').title()}: {desc}" for key, desc in self.knowledge_base["ckd_stages"].items()])
        
        # Check for symptom questions
        if any(symptom_word in message for symptom_word in ["symptom", "sign", "feel"]):
            for symptom_key, description in self.knowledge_base["common_symptoms"].items():
                if symptom_key in message:
                    return description
            return "Common symptoms of CKD include:\n\n" + \
                   "\n".join([f"• {key.replace('_', ' ').title()}: {desc}" for key, desc in self.knowledge_base["common_symptoms"].items()])
        
        # Check for medical term explanations
        for term_key, description in self.knowledge_base["medical_terms"].items():
            if term_key in message.replace(" ", ""):
                return description
        
        # Check for lifestyle questions
        if any(lifestyle_word in message for lifestyle_word in ["diet", "food", "eat", "exercise", "workout", "activity"]):
            return self.knowledge_base["lifestyle"]["diet"]
        
        if any(lifestyle_word in message for lifestyle_word in ["exercise", "workout", "activity", "sport"]):
            return self.knowledge_base["lifestyle"]["exercise"]
        
        if any(lifestyle_word in message for lifestyle_word in ["water", "fluid", "hydrate", "hydration"]):
            return self.knowledge_base["lifestyle"]["hydration"]
        
        if any(lifestyle_word in message for lifestyle_word in ["medicine", "medication", "drug", "pill"]):
            return self.knowledge_base["lifestyle"]["medications"]
        
        # If we can't answer directly, offer to escalate
        escalation_keywords = ["doctor", "appointment", "prescription", "medication change", "urgent", "emergency", "serious"]
        if any(keyword in message for keyword in escalation_keywords):
            return "I understand you may need assistance from a healthcare provider. Please contact your doctor directly for medical advice regarding prescriptions, appointments, or urgent concerns. Would you like me to help with anything else about CKD in the meantime?"
        
        # Default response
        return "I can help you understand more about Chronic Kidney Disease. You can ask me about:\n\n" + \
               "• CKD stages and what they mean\n" + \
               "• Common symptoms to watch for\n" + \
               "• Medical terms related to kidney health\n" + \
               "• Diet and lifestyle recommendations\n\n" + \
               "What would you like to know more about?"
    
    def get_conversation_history(self):
        """Return the conversation history"""
        return self.conversation_history
    
    def reset_conversation(self):
        """Reset the conversation history"""
        self.conversation_history = []
        return "Conversation reset. How can I help you today?"

# Factory function for easy import
def get_patient_chatbot():
    """Factory function to create patient chatbot instance"""
    return PatientEducationChatbot()