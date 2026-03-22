import cv2
import uuid
import logging
import numpy as np
from datetime import datetime
from src.database import DatabaseStore
from src.face_store import FaceStore
from src.detector import FaceDetector
from src.recognizer import FaceRecognizer
from src.tracker import SimpleIoUTracker
from src.registry import IdentityRegistry
from src.event_logger import EventLogger
from src.video_source import VideoSource

logger = logging.getLogger(__name__)

class VisitorPipeline:
    def __init__(self, config: dict):
        self.config = config
        self.db = DatabaseStore(config['db_path'])
        self.face_store = FaceStore(self.db, config['output_root'])
        self.face_store.load_known_faces()
        
        self.detector = FaceDetector(
            model_path=config['detector'].get('model_path', 'models/yolov8n-face.pt'),
            conf_threshold=config['detector'].get('conf_threshold', 0.45),
            input_size=config['detector'].get('input_size', 640)
        )
        self.recognizer = FaceRecognizer(
            model_name=config['recognizer'].get('model_name', 'buffalo_l'),
            providers=config['recognizer'].get('providers', ['CPUExecutionProvider'])
        )
        self.tracker = SimpleIoUTracker(
            max_missing_frames=config['tracker'].get('max_missing_frames', 20),
            iou_threshold=config['tracker'].get('iou_threshold', 0.3)
        )
        self.registry = IdentityRegistry(
            db=self.db,
            face_store=self.face_store,
            recognition_threshold=config['recognizer'].get('recognition_threshold', 0.45)
        )
        self.event_logger = EventLogger(
            db=self.db,
            log_root=config['log_root'],
            save_entry_images=config['logging'].get('save_entry_images', True),
            save_exit_images=config['logging'].get('save_exit_images', True)
        )
        
        self.run_id = f"run_{uuid.uuid4().hex[:8]}"
        self.source_name = config.get('video_source', 'unknown')
        self.frame_skip = config['detector'].get('frame_skip', 3)
        self.min_track_hits = config['tracker'].get('min_track_hits', 3)
        self.max_missing_frames = config['tracker'].get('max_missing_frames', 20)
        
        # Keep KCF trackers for intermediate frames
        self.cv2_trackers = {}

    def get_timestamp(self) -> datetime:
        return datetime.now()

    def process_frame(self, frame: np.ndarray, frame_idx: int) -> np.ndarray:
        timestamp = self.get_timestamp()
        
        if frame_idx % self.frame_skip == 0:
            # -- Detection Frame --
            detections = self.detector.detect(frame)
            self.recognizer.compute_embeddings(frame, detections)
            active_tracks = self.tracker.update(detections, frame_idx)
            
            # Re-initialize intermediate KCF trackers
            self.cv2_trackers.clear()
            for t in active_tracks:
                if t.missing_frames == 0: # just detected
                    x = max(0, int(t.bbox.x1))
                    y = max(0, int(t.bbox.y1))
                    w = max(1, int(t.bbox.x2 - t.bbox.x1))
                    h = max(1, int(t.bbox.y2 - t.bbox.y1))
                    try:
                        # Sometimes MOSSE or KCF is used depending on cv2 version. KCF is generally available.
                        tracker = cv2.TrackerKCF_create()
                        tracker.init(frame, (x, y, w, h))
                        self.cv2_trackers[t.track_id] = tracker
                    except Exception as e:
                        logger.warning(f"Failed to init KCF tracker: {e}")
        else:
            # -- Intermediate Tracking Frame --
            active_tracks = self.tracker.get_active_tracks()
            for t in active_tracks:
                if t.track_id in self.cv2_trackers:
                    ok, box = self.cv2_trackers[t.track_id].update(frame)
                    if ok:
                        x, y, w, h = box
                        t.bbox.x1, t.bbox.y1 = x, y
                        t.bbox.x2, t.bbox.y2 = x + w, y + h
        
        # -- Logic Integration --
        active_tracks = self.tracker.get_active_tracks()
        
        # Handle matching, entries and exits
        for track in active_tracks:
            # Re-identify if hits is sufficient but not yet identified
            if track.identity_id is None and track.hits >= self.min_track_hits:
                self.registry.match_or_register(track, timestamp.isoformat(), self.source_name)
                
            # Log Entry if stable and identified
            if track.identity_id is not None and track.hits >= self.min_track_hits and not track.entered_logged:
                self.event_logger.log_entry(self.run_id, track, timestamp, self.source_name, frame)
                
        # Check for Exits (tracks that are missing for > max_missing_frames)
        # We manually check the internal tracker dict instead of get_active_tracks()
        expired_track_ids = []
        for track_id, track in list(self.tracker.tracks.items()):
            if track.missing_frames > self.max_missing_frames:
                if track.entered_logged and not track.exited_logged:
                    self.event_logger.log_exit(self.run_id, track, timestamp, self.source_name, frame)
                expired_track_ids.append(track_id)
                
        for tid in expired_track_ids:
            self.tracker.remove_track(tid)
            if tid in self.cv2_trackers:
                del self.cv2_trackers[tid]
                
        # Draw visualization
        out_frame = frame.copy()
        for track in active_tracks:
            x1, y1 = int(track.bbox.x1), int(track.bbox.y1)
            x2, y2 = int(track.bbox.x2), int(track.bbox.y2)
            cv2.rectangle(out_frame, (x1, y1), (x2, y2), (0, 255, 0) if track.identity_id else (0, 165, 255), 2)
            
            label = track.identity_id if track.identity_id else f"ID: {track.track_id}"
            cv2.putText(out_frame, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
            
        return out_frame

    def run(self, show_video: bool = True):
        logger.info(f"Starting Run {self.run_id}")
        self.db.insert_run(self.run_id, self.source_name, self.get_timestamp().isoformat())
        
        source = VideoSource(self.source_name)
        
        try:
            for idx, frame in source:
                out_frame = self.process_frame(frame, idx)
                if show_video:
                    # Resize for display if too large
                    h, w = out_frame.shape[:2]
                    if w > 1280:
                        out_frame = cv2.resize(out_frame, (1280, int(h * 1280 / w)))
                    cv2.imshow("Visitor Counter", out_frame)
                    if cv2.waitKey(1) & 0xFF == ord('q'):
                        logger.info("Early exit requested by user.")
                        break
        except Exception as e:
            logger.error(f"Error during video processing: {e}")
        finally:
            source.release()
            try:
                cv2.destroyAllWindows()
            except Exception:
                pass
            # Log any remaining active tracks as exited 
            timestamp = self.get_timestamp()
            for track in self.tracker.get_active_tracks():
                if track.entered_logged and not track.exited_logged:
                    self.event_logger.log_exit(self.run_id, track, timestamp, self.source_name)
                    
            self.db.finalize_run(self.run_id, timestamp.isoformat(), "COMPLETED")
            logger.info(f"Run {self.run_id} finalized.")
