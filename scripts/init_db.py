import sys
import os
import argparse
from pathlib import Path

# Add project root to python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.config_loader import load_config
from src.database import DatabaseStore

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Initialize tracking database")
    parser.add_argument("--config", type=str, default="config.json", help="Path to config file")
    args = parser.parse_args()

    print("Loading config...")
    config = load_config(args.config)
    
    db_path = config.get('db_path', 'data/db/visitor_counter.db')
    print(f"Initializing database at {db_path}...")
    
    db = DatabaseStore(db_path)
    
    print("Database tables created. (identities, identity_embeddings, events, runs)")
    print("Testing basic query...")
    count = db.count_unique_visitors()
    print(f"Current visitor count: {count}")
    print("Initialization complete!")
