import os
import sys

# Add project root to python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.config_loader import load_config
from src.detector import FaceDetector
from src.recognizer import FaceRecognizer

if __name__ == "__main__":
    print("Loading config...")
    config = load_config('config.json')
    
    print("\n[1/2] Verifying YOLO Face Detector...")
    try:
        detector = FaceDetector(
            model_path=config['detector']['model_path'],
            conf_threshold=config['detector']['conf_threshold']
        )
        print("YOLO Detector initialized successfully.")
    except Exception as e:
        print(f"FAILED to initialize YOLO Detector: {e}")
        sys.exit(1)
        
    print("\n[2/2] Verifying InsightFace Recognizer (will download ~330MB if first time)...")
    try:
        recognizer = FaceRecognizer(
            model_name=config['recognizer']['model_name'],
            providers=config['recognizer']['providers']
        )
        print("InsightFace Recognizer initialized successfully.")
    except Exception as e:
        print(f"FAILED to initialize InsightFace Recognizer: {e}")
        print("Troubleshooting: If you see ONNX runtime errors, ensure you have the appropriate execution providers installed.")
        sys.exit(1)
        
    print("\nAll models validated successfully!")
