# Mega AI Real-Time Face Detection Video Streaming System

A containerized backend API and frontend dashboard for real-time face detection, built to fulfill the Mega AI assessment requirements.

## How to Run (in 5 minutes)

1. Ensure Docker and Docker Compose are installed on your machine.
2. Clone this repository.
3. Run the following command from the root of the project:

```bash
docker-compose up --build
```

4. Once the containers are running, open your browser and navigate to:
   **http://localhost:3000**
   
*(Ensure your browser grants webcam permissions when prompted).*

## Architecture & Layers

The system strictly follows a clean, 5-layer separation of concerns:

1. **Layer 1 — Browser (React Frontend):** Captures webcam feed at ~10fps, sends it via WebSocket, receives the MJPEG annotated stream, and polls the database for ROI history. Built with React (Vite) and styled with modern glassmorphic aesthetics.
2. **Layer 2 — API Gateway (FastAPI):** Exposes exactly 3 endpoints:
   - `POST /ws/video-feed` (WebSocket for streaming input)
   - `GET /stream` (MJPEG for streaming output)
   - `GET /roi-data` (REST for historical records)
3. **Layer 3 — Processing Core:** MediaPipe BlazeFace is used for detection (strictly avoiding OpenCV). Pillow (`ImageDraw`) is used to draw the lime-green bounding boxes.
4. **Layer 4 — Database (PostgreSQL):** Uses `asyncpg` and SQLAlchemy async to non-blocking save `roi_events`.
5. **Layer 5 — Infrastructure:** `docker-compose` bridges the Frontend (Nginx), Backend (FastAPI/Uvicorn), and Database (Postgres) networks seamlessly.

## Assessment Constraints Satisfied

- **No OpenCV:** Accomplished via Google's MediaPipe for fast CPU-based detection, combined with Python's native Pillow (PIL) for image manipulation.
- **Strictly 3 Endpoints:** The API surface area is minimal and correct.
- **Containerized:** Fully deployable via a single `docker-compose up` command.
- **Real-Time Data:** Utilizes WebSockets for lowest latency input, and `multipart/x-mixed-replace` for robust browser-native stream rendering.
