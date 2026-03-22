import sqlite3
import logging
from pathlib import Path
from typing import List, Tuple

logger = logging.getLogger(__name__)

class DatabaseStore:
    def __init__(self, db_path: str):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def get_connection(self):
        conn = sqlite3.connect(
            str(self.db_path),
            detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES
        )
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self):
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                # identities
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS identities (
                        identity_id TEXT PRIMARY KEY,
                        first_seen TEXT NOT NULL,
                        last_seen TEXT NOT NULL,
                        preview_image_path TEXT,
                        source_name TEXT
                    )
                """)
                
                # identity_embeddings
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS identity_embeddings (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        identity_id TEXT NOT NULL,
                        embedding_path TEXT NOT NULL,
                        created_at TEXT NOT NULL,
                        FOREIGN KEY(identity_id) REFERENCES identities(identity_id)
                    )
                """)
                
                # events
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS events (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        run_id TEXT NOT NULL,
                        timestamp TEXT NOT NULL,
                        event_type TEXT NOT NULL,
                        identity_id TEXT,
                        track_id TEXT,
                        image_path TEXT,
                        source_name TEXT,
                        notes TEXT
                    )
                """)
                
                # runs
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS runs (
                        run_id TEXT PRIMARY KEY,
                        source_name TEXT NOT NULL,
                        started_at TEXT NOT NULL,
                        ended_at TEXT,
                        status TEXT NOT NULL
                    )
                """)
                
                conn.commit()
        except sqlite3.Error as e:
            logger.error(f"Database initialization error: {e}")
            raise

    def insert_run(self, run_id: str, source_name: str, started_at: str):
        with self.get_connection() as conn:
            conn.execute(
                "INSERT INTO runs (run_id, source_name, started_at, status) VALUES (?, ?, ?, 'RUNNING')",
                (run_id, source_name, started_at)
            )

    def finalize_run(self, run_id: str, ended_at: str, status: str = "COMPLETED"):
        with self.get_connection() as conn:
            conn.execute(
                "UPDATE runs SET ended_at = ?, status = ? WHERE run_id = ?",
                (ended_at, status, run_id)
            )

    def insert_identity(self, identity_id: str, first_seen: str, source_name: str, preview_path: str = None):
        with self.get_connection() as conn:
            conn.execute(
                "INSERT INTO identities (identity_id, first_seen, last_seen, source_name, preview_image_path) VALUES (?, ?, ?, ?, ?)",
                (identity_id, first_seen, first_seen, source_name, preview_path)
            )

    def update_identity_last_seen(self, identity_id: str, last_seen: str):
        with self.get_connection() as conn:
            conn.execute(
                "UPDATE identities SET last_seen = ? WHERE identity_id = ?",
                (last_seen, identity_id)
            )

    def insert_embedding_record(self, identity_id: str, embedding_path: str, created_at: str):
        with self.get_connection() as conn:
            conn.execute(
                "INSERT INTO identity_embeddings (identity_id, embedding_path, created_at) VALUES (?, ?, ?)",
                (identity_id, embedding_path, created_at)
            )

    def insert_event(self, run_id: str, timestamp: str, event_type: str, identity_id: str, track_id: str, image_path: str, source_name: str, notes: str = ""):
        with self.get_connection() as conn:
            conn.execute(
                "INSERT INTO events (run_id, timestamp, event_type, identity_id, track_id, image_path, source_name, notes) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                (run_id, timestamp, event_type, str(identity_id) if identity_id else None, str(track_id) if track_id else None, image_path, source_name, notes)
            )

    def get_all_embeddings(self) -> List[Tuple[str, str]]:
        """Returns list of (identity_id, embedding_path)"""
        with self.get_connection() as conn:
            cursor = conn.execute("SELECT identity_id, embedding_path FROM identity_embeddings")
            return [(row['identity_id'], row['embedding_path']) for row in cursor.fetchall()]

    def count_unique_visitors(self) -> int:
        with self.get_connection() as conn:
            cursor = conn.execute("SELECT COUNT(identity_id) as count FROM identities")
            result = cursor.fetchone()
            return result['count'] if result else 0
