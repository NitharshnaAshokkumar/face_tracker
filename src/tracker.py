import logging
from typing import List, Dict
from src.models import BBox, Detection, Track

logger = logging.getLogger(__name__)

def compute_iou(box1: BBox, box2: BBox) -> float:
    # box1 and box2 intersection
    ix1 = max(box1.x1, box2.x1)
    iy1 = max(box1.y1, box2.y1)
    ix2 = min(box1.x2, box2.x2)
    iy2 = min(box1.y2, box2.y2)

    inter_area = max(0, ix2 - ix1) * max(0, iy2 - iy1)
    if inter_area == 0:
        return 0.0

    box1_area = box1.area
    box2_area = box2.area

    iou = inter_area / float(box1_area + box2_area - inter_area)
    return iou

class SimpleIoUTracker:
    """
    A reliable fallback IoU-based tracker. It assigns track IDs based on 
    spatial overlap. For production/complex scenes, ByteTrack is preferred, 
    but this ensures a lightweight fallback without external C++ dependencies.
    """
    def __init__(self, max_missing_frames: int = 20, iou_threshold: float = 0.3):
        self.max_missing_frames = max_missing_frames
        self.iou_threshold = iou_threshold
        self.tracks: Dict[int, Track] = {}
        self.next_track_id = 1
        
    def update(self, detections: List[Detection], frame_idx: int) -> List[Track]:
        # Simple greedy assignment
        unmatched_tracks = set(self.tracks.keys())
        unmatched_dets = list(range(len(detections)))
        
        # Calculate IoU matrix
        # For small numbers of objects, greedy is fine.
        matches = [] # (track_id, det_idx)
        
        # We sort tracks to ensure determinism
        for track_id in sorted(list(unmatched_tracks)):
            track = self.tracks[track_id]
            best_iou = self.iou_threshold
            best_det_idx = -1
            
            for d_idx in unmatched_dets:
                iou = compute_iou(track.bbox, detections[d_idx].bbox)
                if iou >= best_iou:
                    best_iou = iou
                    best_det_idx = d_idx
                    
            if best_det_idx != -1:
                matches.append((track_id, best_det_idx))
                unmatched_dets.remove(best_det_idx)
                unmatched_tracks.remove(track_id)
                
        # Update matched tracks
        for track_id, d_idx in matches:
            track = self.tracks[track_id]
            det = detections[d_idx]
            
            track.bbox = det.bbox
            track.last_seen_frame = frame_idx
            track.missing_frames = 0
            track.hits += 1
            
            if det.embedding is not None:
                # Naive strategy: just keep the latest embedding, or we could 
                # accumulate and average. Let's keep the most recent good one.
                # A more advanced logic keeps the one with highest quality_score.
                track.best_embedding = det.embedding
                
        # Create new tracks
        for d_idx in unmatched_dets:
            det = detections[d_idx]
            new_track = Track(
                track_id=self.next_track_id,
                bbox=det.bbox,
                last_seen_frame=frame_idx,
                missing_frames=0,
                hits=1,
                best_embedding=det.embedding
            )
            self.tracks[self.next_track_id] = new_track
            self.next_track_id += 1
            
        # Update missing tracks
        for track_id in unmatched_tracks:
            self.tracks[track_id].missing_frames += 1
            
        # Optional: We don't delete tracks here immediately, the pipeline/registry 
        # decides when to call them "expired" and log exits. But we provide an 
        # interface to clean them.
        
        return list(self.tracks.values())
        
    def get_active_tracks(self) -> List[Track]:
        return [t for t in self.tracks.values() if t.missing_frames <= self.max_missing_frames]
        
    def remove_track(self, track_id: int):
        if track_id in self.tracks:
            del self.tracks[track_id]
