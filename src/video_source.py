import cv2
import logging
from typing import Tuple
import numpy as np

logger = logging.getLogger(__name__)

class VideoSource:
    def __init__(self, source_path: str):
        self.source_path = source_path
        self.cap = cv2.VideoCapture(source_path)
        if not self.cap.isOpened():
            logger.error(f"Failed to open video source: {source_path}")
            raise ValueError(f"Could not open source {source_path}")
            
        self.fps = self.cap.get(cv2.CAP_PROP_FPS)
        self.frame_count = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
        self.width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        self.current_frame = 0
        
        logger.info(f"Opened Video Source {self.source_path} (FPS: {self.fps}, Resolution: {self.width}x{self.height}, Total Frames: {self.frame_count})")

    def __iter__(self):
        return self

    def __next__(self) -> Tuple[int, np.ndarray]:
        ret, frame = self.cap.read()
        if not ret:
            raise StopIteration
            
        idx = self.current_frame
        self.current_frame += 1
        return idx, frame

    def release(self):
        if self.cap:
            self.cap.release()
            logger.info("Video source released.")
