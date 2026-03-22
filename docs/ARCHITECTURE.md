# Architecture

## Modularity & Responsibilities

The system is decoupled into the following layers:

1.  **Vision Layer** (`detector.py`, `recognizer.py`, `tracker.py`):
    *   Responsible for receiving RGB frames and outputting bounding boxes and mathematical embeddings. Includes YOLO, InsightFace, and an IoU/KCF tracking system.
2.  **Logic & Matching Layer** (`registry.py`, `face_store.py`):
    *   Takes tracks and determines if they correspond to known `identity_ids` by computing Cosine Similarities against a locally cached `FaceStore` and persisting misses.
3.  **Persistence Layer** (`database.py`, `event_logger.py`):
    *   A robust SQLite wrapper to store events (ENTRY/EXIT) and historical data across application restarts.
4.  **Application Layer** (`pipeline.py`, `app.py`):
    *   Orchestrates the data flow loops.

## Data Flow

```text
Input Video / RTSP Stream
        │
        ▼
   Pipeline.py (Read Frame)
        │
   (If frame_skip == 0)      (Else)
        │                      │
        ▼                      ▼
    YOLO Detector         OpenCV KCF Tracker
        │                      │
        ▼                      │
   InsightFace Embedder        │
        │                      │
        ▼                      ▼
  SimpleIoUTracker (Match detections to existing tracks)
        │
        ▼
 IdentityRegistry (Match embeddings to DB)
        │
        ▼
   EventLogger (Check state, log ENTRY/EXIT via `database.py`)
        │
        ▼
  Output Display / Summary
```
