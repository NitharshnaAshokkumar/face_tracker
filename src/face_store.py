import numpy as np
import logging
from pathlib import Path
from typing import List, Tuple
from src.database import DatabaseStore

logger = logging.getLogger(__name__)

class FaceStore:
    """
    Manages loading and saving embedding vectors from/to disk
    and provides a unified cache of known identities.
    """
    def __init__(self, db_store: DatabaseStore, output_root: str):
        self.db = db_store
        self.output_root = Path(output_root)
        self.embeddings_dir = self.output_root / "embeddings"
        self.embeddings_dir.mkdir(parents=True, exist_ok=True)
        
        # In-memory cache: list of (identity_id, embedding_vector)
        self.known_faces: List[Tuple[str, np.ndarray]] = []
        
    def load_known_faces(self):
        """Loads all configured embeddings from disk and populates cache."""
        self.known_faces.clear()
        records = self.db.get_all_embeddings()
        for identity_id, path_str in records:
            path = Path(path_str)
            if path.exists():
                try:
                    embed = np.load(path)
                    self.known_faces.append((identity_id, embed))
                except Exception as e:
                    logger.error(f"Failed to load embedding {path}: {e}")
            else:
                logger.warning(f"Embedding file missing: {path}")
        logger.info(f"Loaded {len(self.known_faces)} face embeddings from store.")
                
    def save_embedding(self, identity_id: str, embedding: np.ndarray, timestamp: str):
        """
        Writes an embedding vector to a local .npy file and registers it in the DB.
        """
        filename = f"{identity_id}_{timestamp}.npy".replace(":", "-").replace(" ", "_").replace(".", "_")
        filepath = self.embeddings_dir / filename
        try:
            np.save(filepath, embedding)
            # relative path or absolute? Store as string relative to cwd or absolutes. 
            self.db.insert_embedding_record(identity_id, str(filepath), timestamp)
            self.known_faces.append((identity_id, embedding))
        except Exception as e:
            logger.error(f"Failed to save embedding for {identity_id}: {e}")
            
    def get_known_faces(self) -> List[Tuple[str, np.ndarray]]:
        return self.known_faces

    def clean_cache(self):
        self.known_faces.clear()
