from dataclasses import dataclass
from typing import Optional
import numpy as np

@dataclass
class BBox:
    x1: float
    y1: float
    x2: float
    y2: float
    conf: float
    
    @property
    def area(self) -> float:
        return max(0, self.x2 - self.x1) * max(0, self.y2 - self.y1)

@dataclass
class Detection:
    bbox: BBox
    embedding: Optional[np.ndarray] = None
    embedding_norm: float = 0.0

@dataclass
class Track:
    track_id: int
    bbox: BBox
    last_seen_frame: int
    missing_frames: int = 0
    identity_id: Optional[str] = None
    entered_logged: bool = False
    exited_logged: bool = False
    hits: int = 1
    best_embedding: Optional[np.ndarray] = None
    
@dataclass
class IdentityRecord:
    identity_id: str
    first_seen: str
    last_seen: str
    preview_image_path: Optional[str]
    source_name: Optional[str]

@dataclass
class EventRecord:
    run_id: str
    timestamp: str
    event_type: str
    identity_id: str
    track_id: str
    image_path: str
    source_name: str
    notes: str = ""
