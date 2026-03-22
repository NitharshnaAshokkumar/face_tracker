# 🎤 Video Demonstration Script

Use this script to record your **Loom** or **YouTube** project demonstration. Follow the time markers and on-screen instructions for a professional presentation.

---

## 🎬 Part 1: Introduction (0:00 - 0:30)
**On screen**: Show your `README.md` or the Home page of the Streamlit Dashboard.

> "Hello everyone! My name is Nitharshna, and today I’m demonstrating my submission for the hackathon: the **Intelligent Face Tracker with Auto-Registration and Visitor Counting**. 
>
> The goal of this project is to create a robust system that can not only detect faces in real-time but also uniquely identify them, track their entry and exit times, and provide a comprehensive analytics dashboard for managing visitor flow."

---

## 💻 Part 2: Technical Architecture (0:30 - 1:15)
**On screen**: Show the `docs/ARCHITECTURE.md` diagram and the `requirements.txt`.

> "Technically, the system is built using a modular Python pipeline. 
> 1. We use **YOLOv8** for high-speed face detection.
> 2. For identification, we leverage **InsightFace** with the **buffalo_l** model to generate high-dimensional face embeddings.
> 3. We use **Cosine Similarity** to compare these embeddings against our SQLite database. If a face is unrecognized, the system automatically registers them as a new identity.
> 4. To save compute power, we use a hybrid tracking approach: YOLO detects every few frames, while **OpenCV KCF trackers** handle the smooth movement in between."

---

## 📊 Part 3: Dashboard Demo (1:15 - 2:30)
**On screen**: Switch to the **Streamlit Dashboard** (`localhost:8501`). Click through the tabs.

> "Let's look at the web dashboard I built with **Streamlit**. 
>
> *   **Home**: Here we see the live monitoring status and high-level metrics like total unique visitors and recent entries.
> *   **Visitor Gallery**: (Click the Visitors tab) Every unique person detected is stored here as a card. You can see their first and last seen timestamps and even search for specific IDs.
> *   **Event Logs**: (Click the Logs tab) This is where the granular data lives. It shows every entrance and exit, which can be exported directly to CSV for reporting.
> *   **Analytics**: (Click the Analytics tab) We have interactive Plotly charts showing the visitor trends over time."

---

## 🚀 Part 4: Processing Demo (2:30 - 3:30)
**On screen**: Open your terminal and show the app running (`python app.py`). If possible, show the video output window.

> "Here you can see the backend engine in action. As faces move across the screen, the system assigns a stable ID. Notice how it handles 'Entries' only after the face is stabilized, and 'Exits' only after they truly leave the frame. This ensures our visitor count remains accurate and isn't skewed by momentary occlusions."

---

## 🏁 Part 5: Conclusion (3:30+ )
**On screen**: Back to the Dashboard home page or your GitHub repo.

> "This project is fully containerized in a clean repository structure, with complete unit tests and exhaustive documentation. It’s ready for deployment on local workstations or RTSP camera streams.
>
> Thank you for watching, and I look forward to your feedback. This project is a part of a hackathon run by katomaran.com!"

---

## 💡 Recording Tips:
1. **Resolution**: Record in at least 1080p.
2. **Audio**: Use a quiet room and a clear microphone.
3. **Pace**: Speak clearly and don't rush. Pause for a second when switching tabs to let the video catch up.
4. **Tool**: **Loom** is great because it shows your face in a small bubble while you share your screen!
