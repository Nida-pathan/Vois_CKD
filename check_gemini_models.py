"""
Script to list available Gemini models with your API key
"""
import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv('GEMINI_API_KEY')
if not api_key:
    print("ERROR: GEMINI_API_KEY not found in .env file")
    exit(1)

print(f"API Key found: {api_key[:10]}...")
print("\nConfiguring Gemini API...")

try:
    genai.configure(api_key=api_key)
    print("✓ API configured successfully\n")
    
    print("Available models:")
    print("-" * 80)
    
    for model in genai.list_models():
        if 'generateContent' in model.supported_generation_methods:
            print(f"✓ {model.name}")
            print(f"  Display Name: {model.display_name}")
            print(f"  Description: {model.description}")
            print(f"  Supported methods: {', '.join(model.supported_generation_methods)}")
            print()
    
except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()
