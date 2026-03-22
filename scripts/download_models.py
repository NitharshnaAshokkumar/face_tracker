import os
import urllib.request
import logging
import sys

# Add project root to python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def download_file(url, target_path):
    if os.path.exists(target_path):
        logger.info(f"File already exists: {target_path}")
        return True
    logger.info(f"Downloading {url} to {target_path}...")
    try:
        urllib.request.urlretrieve(url, target_path)
        logger.info("Download complete.")
        return True
    except Exception as e:
        logger.error(f"Download failed: {e}")
        return False

if __name__ == "__main__":
    os.makedirs('models', exist_ok=True)
    
    # Popular community yolo-face weights (Lindevs)
    yolo_url = "https://github.com/lindevs/yolov8-face/releases/latest/download/yolov8n-face-lindevs.pt"
    yolo_target = "models/yolov8n-face.pt"
    
    success = download_file(yolo_url, yolo_target)
    
    if not success:
        logger.error(f"Failed to auto-download YOLO. Please download manually from {yolo_url} to {yolo_target}")
        sys.exit(1)
        
    logger.info("InsightFace models (buffalo_l) will be automatically downloaded by the library to ~/.insightface/ on first run.")
