import os
import cv2
import numpy as np
from ultralytics import YOLO

class KidneyStoneYOLO:
    def __init__(self, model_path=None):
        if model_path is None:
            # Default to the path in the models directory
            model_path = os.path.join(os.path.dirname(__file__), 'kidney_stone_yolo_model.pt')
        
        self.model_path = model_path
        self.model = None
        self.load_model()

    def load_model(self):
        try:
            if os.path.exists(self.model_path):
                self.model = YOLO(self.model_path)
                print(f"Kidney Stone YOLO Model loaded successfully from {self.model_path}")
            else:
                print(f"Kidney Stone YOLO Model file not found at {self.model_path}")
        except Exception as e:
            print(f"Error loading Kidney Stone YOLO model: {e}")

    def predict(self, image_path, save_dir='static/predictions'):
        """
        Run inference on an image and return results.
        
        Args:
            image_path (str): Path to the input image.
            save_dir (str): Directory to save the annotated image.
            
        Returns:
            dict: Prediction results including detection status, confidence, and path to results image.
        """
        if self.model is None:
            return {'error': 'Model not loaded', 'disease': 'Kidney Stone', 'stage': 'Error', 'severity': 'Unknown'}

        try:
            # Run inference
            results = self.model(image_path)
            
            # Process results
            detected = False
            confidence = 0.0
            stone_count = 0  # Not applicable for classification
            
            # Result is a list of Results objects
            for r in results:
                # Check if it's a Detection model
                if hasattr(r, 'boxes') and r.boxes is not None:
                    if len(r.boxes) > 0:
                        detected = True
                        stone_count = len(r.boxes)
                        confidences = [box.conf.item() for box in r.boxes]
                        if confidences:
                            confidence = max(confidences)
                
                # Check if it's a Classification model (Likely the case here)
                elif hasattr(r, 'probs') and r.probs is not None:
                    # r.probs is a Probs object
                    # Get the index of the class with highest probability
                    top1_index = r.probs.top1
                    top1_conf = r.probs.top1conf.item()
                    
                    # Get class name
                    class_name = r.names[top1_index]
                    
                    # Log for debugging
                    print(f"YOLO Classification: Class={class_name}, Conf={top1_conf}")
                    
                    # Logic: If class is 'Stone' (or similar), mark as detected
                    # Using loose matching in case of case sensitivity or naming variations
                    if 'stone' in class_name.lower() and 'non' not in class_name.lower():
                        detected = True
                        confidence = top1_conf
                    else:
                        detected = False
                        confidence = 1.0 - top1_conf if top1_conf > 0 else 0.0

            # Save annotated image
            # Create a unique filename for the result
            base_name = os.path.basename(image_path)
            name, ext = os.path.splitext(base_name)
            result_filename = f"{name}_result{ext}"
            
            # Ensure save dir exists
            os.makedirs(save_dir, exist_ok=True)
            result_path = os.path.join(save_dir, result_filename)
            
            # Save the plotted image
            # r.plot() returns a BGR numpy array
            im_array = results[0].plot()  # plot a BGR numpy array of predictions
            cv2.imwrite(result_path, im_array)
            
            # Return standardized format for frontend
            # Convert save path to web-accessible URL path
            web_path = result_path.replace('\\', '/')
            if 'static/' in web_path:
                 web_path = '/' + web_path[web_path.find('static/'):]
            
            if detected:
                risk_level = 'High' if confidence > 0.7 else 'Moderate'
                severity = f"{risk_level} Confidence ({confidence:.1%})"
                recommendations = [
                    "Kidney stone pattern detected in scan.",
                    "Consult a urologist for further imaging (CT KUB) to confirm size/location.",
                    "Maintain hydration.",
                    "Review diet for potential stone-forming foods."
                ]
                stage = "Stone Detected"
            else:
                risk_level = 'Low'
                severity = "Low Risk"
                recommendations = [
                    "No specific kidney stone patterns detected.",
                    "Continue regular health monitoring.",
                    "Maintain good hydration."
                ]
                stage = "Not Detected"

            return {
                'disease': 'Kidney Stone',
                'stage': stage,
                'severity': severity,
                'risk_level': risk_level,
                'confidence': float(confidence),
                'stone_count': stone_count, 
                'image_path': web_path,
                'recommendations': recommendations
            }

        except Exception as e:
            print(f"Prediction error: {e}")
            import traceback
            traceback.print_exc()
            return {'error': str(e), 'disease': 'Kidney Stone', 'stage': 'Error', 'severity': 'Unknown'}

# Initialize instance
kidney_stone_model = KidneyStoneYOLO()
