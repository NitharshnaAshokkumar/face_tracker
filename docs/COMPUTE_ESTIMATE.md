# Compute Estimates

## CPU Estimate

*   **YOLOv8n-face (CPU)**: ~50-80ms per frame.
*   **InsightFace Buffalo_L embedder (CPU)**: ~100-200ms per face crop.
*   **Tracking and Logic**: <5ms per frame.
*   **Total Expected CPU RPS**: If running pure CPU with 3-5 faces, it may take 500ms+ per inference frame. By utilizing the `frame_skip=3` configuration, inference runs every 3rd frame. Intermediate frames use KCF tracker (~2-5ms). Effective frame rate can hover around 8-15 FPS.

## GPU Estimate

*    Requires `onnxruntime-gpu` and `ultralytics` running on CUDA.
*   **YOLOv8n-face (GPU)**: ~10-15ms per frame.
*   **InsightFace_L (GPU)**: ~10-20ms per face crop.
*   **Memory**: ~1.5GB VRAM.
*   Expected real-time 30+ FPS processing with multiple faces even with `frame_skip=1`.

## Storage and Memory

*   `events.log` uses rotating file handlers (10MB max).
*   Vector embeddings (`.npy` files) are ~2KB each. 1,000,000 visitors = 2GB.
*   Entry/Exit cropped images are saved locally depending on configuration (usually ~5KB per crop). This can fill up storage if left running on a very busy camera for months.
*   SQLite DB scales reasonably well up to tens of GBs locally. 

## Bottlenecks & Optimization

*   **Current Bottleneck**: `recognizer.py` running on CPU is the heaviest operation. O(N) naive Euclidean distance checking in Python for similarities will become a bottleneck above 50,000 visitors.
*   **Optimizations for scale**:
    1.  Swap Python array iteration for `FAISS` or `HNSW` vector databases.
    2.  Migrate SQLite to PostgreSQL for concurrent writes.
    3.  Make embedding computation asynchronous (extracting the crop, queueing it to a background worker to not block the main stream display thread).
