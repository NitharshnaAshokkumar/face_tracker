import os
import subprocess
import sys
from pathlib import Path

def main():
    # Get project root (parent directory of /scripts)
    project_root = Path(__file__).parent.parent.absolute()
    os.chdir(project_root)
    
    # Path to streamlit.exe in venv
    if os.name == 'nt':
        streamlit_path = project_root / "venv" / "Scripts" / "streamlit.exe"
    else:
        streamlit_path = project_root / "venv" / "bin" / "streamlit"
        
    if not streamlit_path.exists():
        print(f"Error: Streamlit not found at {streamlit_path}")
        print("Please ensure you have installed dependencies: pip install streamlit")
        sys.exit(1)
        
    print(f"Starting Face Tracker Dashboard from {project_root}...")
    try:
        # Run streamlit app
        subprocess.run([str(streamlit_path), "run", "streamlit_app.py"], check=True)
    except KeyboardInterrupt:
        print("\nUI Stopped.")
    except Exception as e:
        print(f"Failed to start UI: {e}")

if __name__ == "__main__":
    main()
