# Planning & Workflow

## Workflow

1.  **Requirements Analysis**: Analyze the core objectives of the face tracker, auto-registration and counting capabilities.
2.  **Architecture Design**: Structure the code into decoupled modules (Vision vs Logic vs Persistence).
3.  **Component Implementation**:
    *   Database schema setup using SQLite.
    *   YOLO face detector wrapping.
    *   InsightFace embedder implementation.
    *   Simple IoU tracker for fallback tracking.
4.  **Integration**: Assemble these pieces into `pipeline.py`.
5.  **Logging & Resiliency**: Adding the `EventLogger` for clean entry/exits and directory structure creation.
6.  **Refinement**: Tweaking configuration variables like `frame_skip` and logging thresholds.

## Phases

*   **Phase 1: Setup & Database Layer**: Completed. Created models and local SQLite persistence for identities and embeddings.
*   **Phase 2: Vision Pipeline**: Completed. Evaluated YOLO and insightface integration. Set up cropped embedding generation.
*   **Phase 3: Tracker & Logic**: Completed. Reconciled `frame_skip` behavior using OpenCV standard KCF tracker to maintain bboxes on intermediate frames without running YOLO.
*   **Phase 4: Output & Run Apps**: Completed. End-to-end `app.py` created and summary exportation script.

## Risks and Mitigations

*   **Heavy compute**: YOLO + Insightface running every frame is too expensive. *Mitigated* by implementing configurable `frame_skip` combined with `KCF` intermediate trackers.
*   **False matches/High Cosine Similarity for wrong identities**: *Mitigated* by configuring a strict configurable threshold (e.g. `0.45`).
*   **GPU Unavailability**: *Mitigated* by using `onnxruntime` and explicitly backing off to `CPUExecutionProvider` in the configuration. CPU YOLO is fast enough for low-res streams.
