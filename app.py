import argparse
import logging
import sys
from pathlib import Path

from src.config_loader import load_config
from src.utils import setup_logging
from src.pipeline import VisitorPipeline
from src.database import DatabaseStore

def main():
    parser = argparse.ArgumentParser(description="Intelligent Face Tracker")
    parser.add_argument("--config", type=str, default="config.json", help="Path to config.json")
    parser.add_argument("--no-display", action="store_true", help="Run without showing video window")
    args = parser.parse_args()

    try:
        config = load_config(args.config)
        log_file = str(Path(config['log_root']) / "events.log")
        logger = setup_logging(log_file)
        
        logger.info("Initializing Intelligent Face Tracker")
        
        # Ensures basic directories output paths
        Path(config['output_root']).mkdir(parents=True, exist_ok=True)
        Path(config['log_root']).mkdir(parents=True, exist_ok=True)
        
        pipeline = VisitorPipeline(config)
        
        # Display summary before exit
        db = DatabaseStore(config['db_path'])
        initial_count = db.count_unique_visitors()
        
        pipeline.run(show_video=not args.no_display)
        
        final_count = db.count_unique_visitors()
        logger.info(f"Total Unique Visitors processed in this run: {final_count - initial_count}")
        logger.info(f"Total Database Visitors overall: {final_count}")
        print(f"\\n--- RUN SUMMARY ---")
        print(f"Run ID: {pipeline.run_id}")
        print(f"New Unique Identities during this run: {final_count - initial_count}")
        print(f"Total Unique Identities in DB: {final_count}")
        print(f"-------------------\n")
        
    except Exception as e:
        logging.error(f"Fatal error during execution: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
