import logging
import numpy as np
from typing import List
from ultralytics import YOLO
from src.models import BBox, Detection

logger = logging.getLogger(__name__)

class FaceDetector:
    def __init__(self, model_path: str, conf_threshold: float = 0.45, input_size: int = 640):
        self.conf_threshold = conf_threshold
        self.input_size = input_size
        logger.info(f"Loading YOLO Face Detector from {model_path} with conf {conf_threshold}")
        try:
            self.model = YOLO(model_path)
        except Exception as e:
            logger.error(f"Failed to load YOLO model from {model_path}: {e}")
            raise

    def detect(self, frame: np.ndarray) -> List[Detection]:
        """
        Runs YOLO on the given frame and returns a list of Detections.
        """
        results = self.model.predict(
            source=frame,
            conf=self.conf_threshold,
            imgsz=self.input_size,
            verbose=False
        )
        
        detections = []
        for result in results:
            boxes = result.boxes
            if boxes is None or len(boxes) == 0:
                continue
                
            for box in boxes:
                # box.xyxy is shape (1, 4)
                x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                conf = float(box.conf[0].cpu().numpy())
                
                # YOLO might detect multiple classes, but if it's a specific face model,
                # we assume all outputs over threshold are faces. We could filter by box.cls if needed.
                bbox = BBox(x1=float(x1), y1=float(y1), x2=float(x2), y2=float(y2), conf=conf)
                detections.append(Detection(bbox=bbox))
                
        return detections
