# Intelligent Face Tracker with Auto-Registration

A robust, hackathon-ready Face Tracking, Identification, and Visitor Counting pipeline. It ingests video files or RTSP streams, automatically assigns unique `identity_id`s to unseen faces, and comprehensively logs ENTRY and EXIT events into an SQLite database.

## Features

- **Face Detection**: Uses YOLO (yolov8n-face) for rapid, accurate bounding boxes.
- **Deep Feature Embeddings**: Uses InsightFace (buffalo_l) to encode cropped faces into high-dimensional vectors.
- **Auto-Registration**: Computes Cosine Similarity against recognized historical vectors. If distance is above a threshold, matches; otherwise, registers a new visitor.
- **Robust Tracking**: Implements an IoU-based tracker assisted by OpenCV KCF trackers for intermediate un-detected frames (`frame_skip` functionality) saving extensive compute.
- **Event Logging**: Logs exact `ENTRY` and `EXIT` events for tracking stability, avoiding duplicate unique visitor counts.

## Video Demonstration

  https://drive.google.com/file/d/1ZV3TQM0kmPsCQbKJzA1wTzpxlzBukVvN/view

## Setup Instructions

### 1. Requirements

Ensure you are using **Python 3.10+**.

```bash
git clone <this-repository>
cd face-visitor-counter
python -m venv venv
# Windows
venv\\Scripts\\activate
# Linux/Mac
source venv/bin/activate

pip install -r requirements.txt
```

### 2. Download and Verify Models

Run the automatic model downloader and verification script:
```bash
python scripts/download_models.py
python scripts/verify_models.py
```

- **YOLO Face**: The script attempts to download `yolov8n-face.pt` into the `models/` directory. If it fails due to network issues, manually download it from [GitHub Releases](https://github.com/lindevs/yolov8-face/releases/latest/download/yolov8n-face-lindevs.pt) and place it at `models/yolov8n-face.pt`.
- **InsightFace**: During `verify_models.py`, InsightFace will automatically download the `buffalo_l` model weights to `~/.insightface/` (approx 330MB).

### 3. Quickstart & Demo

Before running the application, prepare your config and initialize the database.

```bash
# 1. Provide a dummy video file and edit config.json to point to it:
# "video_source": "data/input/sample.mp4"

# 2. Initialize the DB
python scripts/init_db.py --config config.json

# 3. Run the application
python app.py --config config.json

# 4. Export run summary
python scripts/export_summary.py
```

### 4. Web Dashboard (Recommended)

To view visitor analytics, the identity gallery, and real-time event logs in a beautiful modern interface, launch the Streamlit dashboard:

```bash
python scripts/run_ui.py
```

**Features:**
- **Dashboard**: Real-time summary cards and monitoring status.
- **Visitor Gallery**: Searchable cards for every unique person detected, with photos.
- **Event Logs**: Detailed ENTRY/EXIT history with CSV export functionality.
- **Analytics**: Trend charts for visitor flow and activity.
- **Config**: Edit system thresholds and video sources directly from the UI.


### 4. Running with RTSP

To run with a live IP camera stream, simply modify your `config.json`:

```json
{
  "video_source": "rtsp://username:password@192.168.1.100:554/stream1",
  "source_type": "rtsp"
}
```

## 📂 Folder Structure

```
face-visitor-counter/
├── app.py                      # Main entrypoint (CLI)
├── streamlit_app.py            # Main entrypoint (Web Dashboard)
├── config.json                 # Configuration parameters
├── requirements.txt            # Python dependencies
├── src/                        # Main logic modules
│   ├── pipeline.py             # Orchestrates the logic
│   ├── detector.py             # YOLO Face Wrapper
│   ├── recognizer.py           # InsightFace Wrapper
│   ├── registry.py             # Matches Tracks against DB
│   ├── tracker.py              # IoU & BBox Tracker
│   ├── ui_helpers.py           # Dashboard Data Helpers
│   ├── database.py             # SQLite interface
│   └── ...
├── scripts/                    # Helper scripts
│   ├── init_db.py              # DB Initialization
│   ├── download_models.py      # Dependency setup
│   ├── run_ui.py               # Dashboard Launcher
│   └── export_summary.py       # CLI Summary
├── docs/                       # Planning & Architecture
└── tests/                      # Pytest cases
```

## 📝 AI Planning & Architecture
This project followed a rigorous design phase:
- **[AI Planning Document](docs/PLANNING.md)**: Detailed breakdown of the phased implementation strategy.
- **[Architecture Diagram](docs/ARCHITECTURE.md)**: Visual representation of the data flow from video source to identified events.
- **[Compute Estimates](docs/COMPUTE_ESTIMATE.md)**: Performance analysis for CPU/GPU targets.

## 💡 Assumptions
- A sufficiently illuminated, mostly forward-facing capture geometry exists.
- Running without a GPU leverages the OpenCV KCF tracker tightly bounding YOLO detection limits for smooth 10fps+ behavior on CPU.
- Config correctly aligns with absolute/relative OS-agnostic `pathlib` resolutions.

## ⚙️ Sample `config.json` Structure
```json
{
  "video_source": "data/input/sample.mp4",
  "source_type": "video",
  "db_path": "data/db/visitor_counter.db",
  "log_root": "logs",
  "output_root": "data/output",
  "detector": {
    "model_path": "models/yolov8n-face.pt",
    "conf_threshold": 0.45,
    "frame_skip": 3
  },
  "recognizer": {
    "model_name": "buffalo_l",
    "recognition_threshold": 0.45
  }
}
```

## 🎤 Interview & Discussion Points
*   **Why SQLite?**: Simple zero-setup persistence for a hackathon. Easily upgradable to Postgres.
*   **How does Entry/Exit work?**: Avoids duplicate counts by requiring a stabilization period (`min_track_hits`) and a timeout period (`max_missing_frames`).
*   **Unique Visitor Logic**: Every face is mapped to a high-dimensional embedding. We use Cosine Similarity to compare new detections against all registered identities in the DB.

## 🛠️ Troubleshooting
- `FileNotFoundError`: Ensure you are running scripts from the root directory.
- `CV2 assertion error`: Check your video path in `config.json`.

---

This project is a part of a hackathon run by https://katomaran.com
