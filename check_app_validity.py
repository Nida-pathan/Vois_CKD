import sys
import os

# Add current directory to path
sys.path.append(os.getcwd())

try:
    from app import app
    print("SUCCESS: app.py imported successfully.")
except Exception as e:
    print(f"FAILURE: Could not import app.py. Error: {e}")
    import traceback
    traceback.print_exc()
