
import os
import sys

# Force unbuffered output
sys.stdout.reconfigure(line_buffering=True)
sys.stderr.reconfigure(line_buffering=True)

# Add project root to path
sys.path.append(os.getcwd())

print("Starting verification script...", flush=True)

try:
    from models.patient_chatbot import get_patient_chatbot
    from datetime import datetime

    print("1. Initializing Chatbot...", flush=True)
    chatbot = get_patient_chatbot()
    
    if chatbot.rag_enabled:
        print("   ✅ RAG Engine enabled")
    else:
        print("   ❌ RAG Engine FAILED (Check logs)")

    print("\n2. Testing Message Processing...")
    # Test a question that relies on the sample knowledge base
    question = "What are the sodium limits for CKD?"
    print(f"   User Question: {question}")
    
    # Mock patient data
    patient_data = {
        'age': 45,
        'stage': 'Stage 3b',
        'egfr': 35,
        'symptoms': {'fatigue': 1}
    }
    
    response = chatbot.process_message(question, patient_data)
    print(f"\n   Bot Response: {response}")
    
    if "2,300 mg" in response or "sodium" in response.lower():
        print("\n   ✅ Response seems relevant (contains keywords from sample doc)")
    else:
        print("\n   ⚠️ Response might not be using context correctly")

    print("\n3. Testing Context Awareness...")
    question2 = "Can I eat bananas?"
    # Mock patient with high potassium
    patient_data_high_k = {
        'potassium': 5.5, # High
        'stage': 'Stage 3b'
    }
    print(f"   User Question: {question2} (Patient K=5.5)")
    response2 = chatbot.process_message(question2, patient_data_high_k)
    print(f"\n   Bot Response: {response2}")

except Exception as e:
    print(f"\n❌ FATAL ERROR: {e}")
    import traceback
    traceback.print_exc()
