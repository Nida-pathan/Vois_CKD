import joblib
import pickle
import os
import sys
import pandas as pd
import numpy as np

model_dir = r"c:\Users\Rajea\OneDrive\Desktop\VOIS\Vois_CKD\models"
files = ["ckd_model.pkl", "aki_detection_model.pkl", "esrd_detection_model.pkl"]

def inspect_model(filename):
    path = os.path.join(model_dir, filename)
    print(f"\n--- Inspecting {filename} ---")
    try:
        try:
            model = joblib.load(path)
            print("Loaded with joblib")
        except:
            with open(path, 'rb') as f:
                model = pickle.load(f)
            print("Loaded with pickle")
            
        print(f"Type: {type(model)}")
        
        if hasattr(model, 'n_features_in_'):
            print(f"Expected features: {model.n_features_in_}")
        
        if hasattr(model, 'feature_names_in_'):
            print(f"Feature names: {model.feature_names_in_}")
        elif hasattr(model, 'steps'): # Pipeline
            print("Is Pipeline")
            # Try to find the step with feature names
            for name, step in model.steps:
                print(f"Step: {name}, Type: {type(step)}")
                if hasattr(step, 'n_features_in_'):
                    print(f"  Expected features: {step.n_features_in_}")
                if hasattr(step, 'feature_names_in_'):
                    print(f"  Feature names: {step.feature_names_in_}")
                    
    except Exception as e:
        print(f"Error loading {filename}: {e}")

# Only run the inspection when the script is executed directly, not when imported
if __name__ == "__main__":
    for f in files:
        inspect_model(f)