import asyncio
import itertools
import logging
import uuid
from contextlib import asynccontextmanager
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession

from . import models, schemas, crud, database
from .frame_processor import process_frame

logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    yield

app = FastAPI(title="Mega AI Face Detection API", lifespan=lifespan)

# Allow CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global set of subscriber queues for MJPEG streaming
subscribers = set()
_frame_counter = itertools.count(1)

async def broadcast_frame(frame_bytes: bytes):
    for q in subscribers:
        try:
            if q.full():
                q.get_nowait() # drop old frame if queue full
            q.put_nowait(frame_bytes)
        except Exception:
            pass

@app.websocket("/ws/video-feed")
async def video_feed(websocket: WebSocket, db: AsyncSession = Depends(database.get_db)):
    session_id = uuid.uuid4()
    await websocket.accept()
    logger.info(f"WebSocket client connected with session {session_id}")
    try:
        while True:
            # Receive JPEG bytes from frontend
            frame_bytes = await websocket.receive_bytes()
            if len(frame_bytes) > 2 * 1024 * 1024:  # 2MB cap
                logger.warning(f"Frame exceeded 2MB limit in session {session_id}")
                await websocket.close(code=1009)
                return

            frame_id = next(_frame_counter)
            
            # Process the frame (detect & annotate)
            annotated_bytes, roi = process_frame(frame_bytes)
            
            # Broadcast annotated frame to MJPEG stream clients
            await broadcast_frame(annotated_bytes)
            
            # Store ROI in database
            if roi:
                try:
                    roi_data = schemas.RoiEventCreate(
                        session_id=session_id,
                        frame_id=frame_id,
                        x=roi['x'],
                        y=roi['y'],
                        w=roi['w'],
                        h=roi['h'],
                        confidence=roi['confidence']
                    )
                    await crud.create_roi_event(db, roi_data)
                except Exception as e:
                    logger.error(f"Error saving ROI to DB: {e}")
                
    except WebSocketDisconnect:
        logger.info(f"WebSocket client disconnected for session {session_id}")
    except Exception as e:
        logger.error(f"Error in websocket loop for session {session_id}: {e}")

async def mjpeg_generator():
    q = asyncio.Queue(maxsize=2)
    subscribers.add(q)
    try:
        while True:
            frame = await q.get()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
    finally:
        subscribers.remove(q)

@app.get("/stream")
async def stream():
    return StreamingResponse(mjpeg_generator(), media_type="multipart/x-mixed-replace; boundary=frame")

@app.get("/roi-data", response_model=list[schemas.RoiEvent])
async def get_roi_data(limit: int = 50, offset: int = 0, db: AsyncSession = Depends(database.get_db)):
    events = await crud.get_roi_events(db, limit=limit, offset=offset)
    return events
