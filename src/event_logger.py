import cv2
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional
import numpy as np
from src.models import Track
from src.database import DatabaseStore

logger = logging.getLogger(__name__)

class EventLogger:
    def __init__(self, db: DatabaseStore, log_root: str, save_entry_images: bool = True, save_exit_images: bool = True):
        self.db = db
        self.log_root = Path(log_root)
        self.save_entry_images = save_entry_images
        self.save_exit_images = save_exit_images
        
        self.entries_dir = self.log_root / "entries"
        self.exits_dir = self.log_root / "exits"
        self.entries_dir.mkdir(parents=True, exist_ok=True)
        self.exits_dir.mkdir(parents=True, exist_ok=True)

    def _get_daily_dir(self, base_dir: Path, timestamp: datetime) -> Path:
        date_str = timestamp.strftime("%Y-%m-%d")
        daily_dir = base_dir / date_str
        daily_dir.mkdir(exist_ok=True)
        return daily_dir
        
    def _save_crop(self, frame: np.ndarray, track: Track, save_dir: Path, timestamp: datetime) -> Optional[str]:
        if frame is None or frame.size == 0:
            return None
            
        h, w = frame.shape[:2]
        x1 = max(0, int(track.bbox.x1))
        y1 = max(0, int(track.bbox.y1))
        x2 = min(w, int(track.bbox.x2))
        y2 = min(h, int(track.bbox.y2))
        
        if x2 <= x1 or y2 <= y1:
            return None
            
        crop = frame[y1:y2, x1:x2]
        if crop.size > 0:
            filename = f"{track.identity_id}_{timestamp.strftime('%H%M%S')}_{track.track_id}.jpg"
            save_path = save_dir / filename
            cv2.imwrite(str(save_path), crop)
            return str(save_path)
            
        return None

    def log_entry(self, run_id: str, track: Track, timestamp: datetime, source_name: str, frame: np.ndarray = None):
        if track.entered_logged:
            return
            
        image_path = ""
        if self.save_entry_images and frame is not None:
            daily_dir = self._get_daily_dir(self.entries_dir, timestamp)
            saved = self._save_crop(frame, track, daily_dir, timestamp)
            image_path = saved if saved else ""
            
        ts_str = timestamp.isoformat()
        self.db.insert_event(
            run_id=run_id,
            timestamp=ts_str,
            event_type="ENTRY",
            identity_id=track.identity_id,
            track_id=str(track.track_id),
            image_path=image_path,
            source_name=source_name,
            notes=f"Track {track.track_id} entered"
        )
        logger.info(f"ENTRY: Identity {track.identity_id} (Track {track.track_id}) at {ts_str}")
        track.entered_logged = True

    def log_exit(self, run_id: str, track: Track, timestamp: datetime, source_name: str, frame: np.ndarray = None):
        if track.exited_logged:
            return
            
        image_path = ""
        if self.save_exit_images and frame is not None:
            daily_dir = self._get_daily_dir(self.exits_dir, timestamp)
            saved = self._save_crop(frame, track, daily_dir, timestamp)
            image_path = saved if saved else ""
            
        ts_str = timestamp.isoformat()
        self.db.insert_event(
            run_id=run_id,
            timestamp=ts_str,
            event_type="EXIT",
            identity_id=track.identity_id,
            track_id=str(track.track_id),
            image_path=image_path,
            source_name=source_name,
            notes=f"Track {track.track_id} exited"
        )
        logger.info(f"EXIT: Identity {track.identity_id} (Track {track.track_id}) at {ts_str}")
        track.exited_logged = True
