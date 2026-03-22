import os
import pandas as pd
import sqlite3
from pathlib import Path
from datetime import datetime
from src.database import DatabaseStore

class UIHelper:
    def __init__(self, db_path: str, log_root: str):
        self.db_path = db_path
        self.log_root = Path(log_root)
        self.db = DatabaseStore(db_path)

    def get_summary_stats(self):
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            
            # Total unique visitors
            cursor.execute("SELECT COUNT(*) FROM identities")
            unique_visitors = cursor.fetchone()[0]
            
            # Total entries
            cursor.execute("SELECT COUNT(*) FROM events WHERE event_type = 'ENTRY'")
            total_entries = cursor.fetchone()[0]
            
            # Total exits
            cursor.execute("SELECT COUNT(*) FROM events WHERE event_type = 'EXIT'")
            total_exits = cursor.fetchone()[0]
            
            # Last process timestamp
            cursor.execute("SELECT MAX(timestamp) FROM events")
            last_ts = cursor.fetchone()[0]
            
        return {
            "unique_visitors": unique_visitors,
            "total_entries": total_entries,
            "total_exits": total_exits,
            "last_timestamp": last_ts if last_ts else "No data"
        }

    def get_recent_events(self, limit: int = 20):
        query = """
        SELECT e.id, e.timestamp, e.event_type, e.identity_id, e.track_id, e.source_name
        FROM events e
        ORDER BY e.timestamp DESC
        LIMIT ?
        """
        with self.db.get_connection() as conn:
            df = pd.read_sql_query(query, conn, params=(limit,))
        return df

    def get_visitor_gallery(self):
        query = """
        SELECT i.identity_id, i.first_seen, i.last_seen, i.source_name,
               (SELECT COUNT(*) FROM events WHERE identity_id = i.identity_id) as event_count
        FROM identities i
        ORDER BY i.last_seen DESC
        """
        with self.db.get_connection() as conn:
            df = pd.read_sql_query(query, conn)
        return df

    def get_analytics_data(self):
        query = """
        SELECT DATE(timestamp) as date, event_type, COUNT(*) as count
        FROM events
        GROUP BY DATE(timestamp), event_type
        ORDER BY date ASC
        """
        with self.db.get_connection() as conn:
            df = pd.read_sql_query(query, conn)
        return df

    def find_thumbnail(self, identity_id: str, event_type: str = "ENTRY"):
        # Search in logs/entries or logs/exits
        folder = "entries" if event_type == "ENTRY" else "exits"
        search_dir = self.log_root / folder
        
        if not search_dir.exists():
            return None
            
        # Look for files containing identity_id
        # Structure is usually logs/entries/YYYY-MM-DD/identity_id_...jpg
        for date_dir in search_dir.iterdir():
            if date_dir.is_dir():
                for img_path in date_dir.glob(f"*{identity_id}*.jpg"):
                    return str(img_path)
        return None
