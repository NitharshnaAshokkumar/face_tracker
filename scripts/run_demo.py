import sys
import os

# Add project root to python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import main

if __name__ == "__main__":
    print("====================================")
    print(" INTELLIGENT FACE TRACKER DEMO RUN")
    print("====================================")
    print("This will process the video_source specified in config.json")
    print("Press 'q' in the video window to stop.")
    
    # Normally we run via app.py, this is just an alias for demo convenience
    # We could simulate downloading a sample video here if it's missing, but 
    # relying on config is safer.
    
    sys.exit(main())
