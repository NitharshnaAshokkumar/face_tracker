import logging
import numpy as np
from typing import List, Optional
from insightface.app import FaceAnalysis
from src.models import Detection

logger = logging.getLogger(__name__)

class FaceRecognizer:
    """
    Uses InsightFace FaceAnalysis pipeline under the hood, but can be targeted 
    to extract embeddings from pre-cropped regions or full frames if necessary.
    """
    def __init__(self, model_name: str = 'buffalo_l', providers: List[str] = None):
        if providers is None:
            providers = ['CPUExecutionProvider']
            
        logger.info(f"Initializing InsightFace recognizer ({model_name}) with providers {providers}")
        self.app = FaceAnalysis(name=model_name, providers=providers)
        # Using a default ctx_id=0 for GPU if available, else -1 for CPU. 
        # The FaceAnalysis wrapper handles this partially but we configure it specifically.
        
        try:
            ctx_id = 0 if 'CUDAExecutionProvider' in providers else -1
            self.app.prepare(ctx_id=ctx_id, det_size=(640, 640))
        except Exception as e:
            logger.error(f"Failed to prepare InsightFace models: {e}")
            raise

    def get_embedding_from_crop(self, crop: np.ndarray) -> Optional[np.ndarray]:
        """
        Extracts an embedding directly from a cropped face image.
        Uses the recognition module of the loaded pipeline.
        InsightFace models usually expect 112x112 crops.
        """
        if crop.size == 0:
            return None
            
        # We need to detect 5-points in the crop to align it before embedding
        # However, for pure flexibility, we can run the whole app.get() on the crop.
        # This will detect the face INSIDE the crop and align it.
        # If no face is found in the crop by InsightFace, it returns no embedding.
        
        try:
            faces = self.app.get(crop)
            if faces:
                # Take the most central/largest face in the crop
                # The returned face object has .embedding
                best_face = max(faces, key=lambda f: (f.bbox[2]-f.bbox[0])*(f.bbox[3]-f.bbox[1]))
                normed_embedding = best_face.normed_embedding
                return normed_embedding
        except Exception as e:
            logger.warning(f"Error extracting embedding from crop: {e}")
            pass
            
        return None

    def compute_embeddings(self, frame: np.ndarray, detections: List[Detection]) -> None:
        """
        Given a full frame and external detections, crop each bounding box 
        and try to compute an embedding. Updates the Detection objects in-place.
        """
        h, w = frame.shape[:2]
        for det in detections:
            x1 = max(0, int(det.bbox.x1))
            y1 = max(0, int(det.bbox.y1))
            x2 = min(w, int(det.bbox.x2))
            y2 = min(h, int(det.bbox.y2))
            
            # Slightly expand crop to ensure InsightFace can detect landmarks inside
            margin_x = int((x2 - x1) * 0.2)
            margin_y = int((y2 - y1) * 0.2)
            
            cx1 = max(0, x1 - margin_x)
            cy1 = max(0, y1 - margin_y)
            cx2 = min(w, x2 + margin_x)
            cy2 = min(h, y2 + margin_y)
            
            crop = frame[cy1:cy2, cx1:cx2]
            if crop.size == 0 or crop.shape[0] < 20 or crop.shape[1] < 20:
                continue
                
            embed = self.get_embedding_from_crop(crop)
            if embed is not None:
                det.embedding = embed
                det.embedding_norm = np.linalg.norm(embed)
