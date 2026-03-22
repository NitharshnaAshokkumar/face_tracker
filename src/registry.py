import uuid
import logging
from src.database import DatabaseStore
from src.face_store import FaceStore
from src.models import Track
from src.utils import compute_cosine_similarity

logger = logging.getLogger(__name__)

class IdentityRegistry:
    """
    Responsible for matching tracked faces to known identities or 
    registering new identities.
    """
    def __init__(self, db: DatabaseStore, face_store: FaceStore, recognition_threshold: float = 0.45):
        self.db = db
        self.face_store = face_store
        self.recognition_threshold = recognition_threshold
        
    def match_or_register(self, track: Track, timestamp: str, source_name: str) -> str:
        """
        Returns the identity_id for the given track. If matched, updates last_seen.
        If unknown, registers a new identity.
        """
        # If already assigned an identity, just update last seen.
        if track.identity_id is not None:
            self.db.update_identity_last_seen(track.identity_id, timestamp)
            return track.identity_id
            
        embed = track.best_embedding
        if embed is None:
            # Cannot register/match without an embedding
            return None
            
        best_sim = -1.0
        best_id = None
        
        # O(N) naive matching. Fine for thousands of faces. 
        # Use FAISS or HNSW for million-scale.
        for identity_id, known_embed in self.face_store.get_known_faces():
            sim = compute_cosine_similarity(embed, known_embed)
            if sim > best_sim:
                best_sim = sim
                best_id = identity_id
                
        if best_sim >= self.recognition_threshold and best_id is not None:
            # Matched
            logger.info(f"Matched track {track.track_id} with identity {best_id} (sim: {best_sim:.3f})")
            track.identity_id = best_id
            self.db.update_identity_last_seen(best_id, timestamp)
            return best_id
            
        # Register new
        new_id = f"id_{uuid.uuid4().hex[:8]}"
        logger.info(f"Registered NEW identity {new_id} for track {track.track_id} (best sim: {best_sim:.3f})")
        track.identity_id = new_id
        
        # Save to DB and face_store
        self.db.insert_identity(new_id, first_seen=timestamp, source_name=source_name)
        self.face_store.save_embedding(new_id, embed, timestamp)
        
        # It's a new unique visitor, we might log that separately 
        return new_id
