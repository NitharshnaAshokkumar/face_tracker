import pytest
import tempfile
import os
import sys

# Add project root to python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.database import DatabaseStore

def test_db_initialization_and_inserts():
    with tempfile.NamedTemporaryFile('w', delete=False) as f:
        temp_name = f.name
    try:
        db = DatabaseStore(temp_name)
        
        # Test identity insert
        db.insert_identity("id_123", "2023-01-01T12:00:00", "test_source")
        count = db.count_unique_visitors()
        assert count == 1
        
        db.insert_event("run_1", "2023-01-01T12:00:01", "ENTRY", "id_123", "trk_1", "", "test_source")
        
        with db.get_connection() as conn:
            cursor = conn.execute("SELECT * FROM events")
            rows = cursor.fetchall()
            assert len(rows) == 1
            assert rows[0]['event_type'] == 'ENTRY'
            
    finally:
        try:
            import gc
            gc.collect()
            os.remove(temp_name)
        except OSError:
            pass
