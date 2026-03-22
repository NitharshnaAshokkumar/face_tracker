import sys
import os
import argparse

# Add project root to python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.config_loader import load_config
from src.database import DatabaseStore

def export_summary(config_path, output_csv="summary_export.csv"):
    config = load_config(config_path)
    db = DatabaseStore(config['db_path'])
    
    total_visitors = db.count_unique_visitors()
    print(f"Overall Total Unique Visitors: {total_visitors}")
    
    print("\nRecent Events Summary:")
    with db.get_connection() as conn:
        cursor = conn.execute("SELECT timestamp, event_type, identity_id, source_name FROM events ORDER BY timestamp DESC LIMIT 20")
        rows = cursor.fetchall()
        for row in rows:
            print(f"[{row['timestamp']}] {row['event_type']} - Identity: {row['identity_id']} (Source: {row['source_name']})")
        if not rows:
            print("No events logged yet.")
            
    print("\nRecent Runs Summary:")
    with db.get_connection() as conn:
        cursor = conn.execute("SELECT run_id, started_at, ended_at, status FROM runs ORDER BY started_at DESC LIMIT 5")
        rows = cursor.fetchall()
        for row in rows:
            print(f"Run {row['run_id']} | Status: {row['status']} | Started: {row['started_at']} | Ended: {row['ended_at']}")
        if not rows:
            print("No runs logged yet.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default="config.json")
    args = parser.parse_args()
    export_summary(args.config)
