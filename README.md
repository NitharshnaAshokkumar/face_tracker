# Intelligent Face Tracker with Auto-Registration

A robust, hackathon-ready Face Tracking, Identification, and Visitor Counting pipeline. It ingests video files or RTSP streams, automatically assigns unique `identity_id`s to unseen faces, and comprehensively logs ENTRY and EXIT events into an SQLite database.

## Features

- **Face Detection**: Uses YOLO (yolov8n-face) for rapid, accurate bounding boxes.
- **Deep Feature Embeddings**: Uses InsightFace (buffalo_l) to encode cropped faces into high-dimensional vectors.
- **Auto-Registration**: Computes Cosine Similarity against recognized historical vectors. If distance is above a threshold, matches; otherwise, registers a new visitor.
- **Robust Tracking**: Implements an IoU-based tracker assisted by OpenCV KCF trackers for intermediate un-detected frames (`frame_skip` functionality) saving extensive compute.
- **Event Logging**: Logs exact `ENTRY` and `EXIT` events for tracking stability, avoiding duplicate unique visitor counts.

## Video Demonstration

**[ADD YOUR VIDEO LINK HERE]**

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

## Folder Structure

```
face-visitor-counter/
├── app.py                      # Main entrypoint
├── config.json                 # Configuration parameters
├── requirements.txt            # Python dependencies
├── src/                        # Main logic modules
│   ├── config_loader.py
│   ├── pipeline.py             # Orchestrates the logic
│   ├── detector.py             # YOLO Face Wrapper
│   ├── recognizer.py           # InsightFace Wrapper
│   ├── registry.py             # Matches Tracks against DB
│   ├── tracker.py              # IoU & BBox Tracker
│   ├── event_logger.py         # Logs ENTRY/EXIT metrics
│   ├── video_source.py         # Handles MP4 / RTSP
│   ├── database.py             # SQLite interface
│   ├── face_store.py           # Loads/Saves embeddings locally
│   └── utils.py                # Logging & Math helper
├── data/
│   ├── db/                     # SQLite files
│   ├── input/                  # Sample inputs
│   └── output/embeddings       # Stored `.npy` face matrices
├── scripts/                    # Helper scripts
│   ├── init_db.py
│   ├── run_demo.py
│   └── export_summary.py
├── docs/                       # Architecture & design info
└── tests/                      # Pytest cases
```

## Documentation References
For deep dives into our engineering process, please refer to:
- **[Planning Details](docs/PLANNING.md)**: Our step-by-step phased approach and mitigations.
- **[Architecture Details](docs/ARCHITECTURE.md)**: Contains the full modular tracking diagram.
- **[Compute Estimates](docs/COMPUTE_ESTIMATE.md)**: Detailed statistics on CPU/GPU expected workloads.

## Assumptions
- A sufficiently illuminated, mostly forward-facing capture geometry exists.
- Running without a GPU leverages the OpenCV KCF tracker tightly bounding YOLO detection limits for smooth 10fps+ behavior on CPU.
- Config correctly aligns with absolute/relative OS-agnostic `pathlib` resolutions.

## Configuration Basics (`config.json`)
The application is highly dynamically configured at runtime. A typical `config.json` parameter set:
```json
{
  "video_source": "data/input/sample.mp4",
  "db_path": "data/db/visitor_counter.db",
  "log_root": "logs",
  "output_root": "data/output",
  "detector": {
    "model_path": "models/yolov8n-face.pt",
    "conf_threshold": 0.45,
    "frame_skip": 3
  }
}
```

## Interview & Discussion Points

*   **Why SQLite?**: Simple zero-setup persistence for a hackathon. Easily upgradable to Postgres by swapping out `database.py` logic.
*   **Why not pure ByteTrack?**: Compiling custom C++ lapjv/ByteTrack dependencies cross-platform often burns time during hackathons and demos. A robust multi-tracker mixing deterministic IoU with KCF provides almost identical stability without the deployment nightmare.
*   **How does Entry/Exit work?**: An object is only logged as an `ENTRY` when it stabilizes (`min_track_hits`). It's only logged as an `EXIT` when it has gone missing for `max_missing_frames`. The overall visitor count is strictly tied to `IdentityID` persistence, so re-entries don't corrupt the dashboard metrics.

## Troubleshooting

- `FileNotFoundError: Config file not found`: Ensure you are running scripts from the root directory of the repository.
- `CV2 assertion error`: Your video file or camera path is incorrectly configured in `config.json`.
- `InsightFace fails to execute on CPU`: Ensure `CPUExecutionProvider` is correctly listed in `config.json` rather than CUDA, if you lack a GPU.

---

This project is a part of a hackathon run by https://katomaran.com
