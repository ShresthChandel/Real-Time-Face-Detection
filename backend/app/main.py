import asyncio
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession

from . import models, schemas, crud, database
from .frame_processor import process_frame

app = FastAPI(title="Mega AI Face Detection API")

# Allow CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global set of subscriber queues for MJPEG streaming
subscribers = set()
frame_counter = 0

@app.on_event("startup")
async def startup():
    async with database.engine.begin() as conn:
        await conn.run_sync(models.Base.metadata.create_all)

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
    global frame_counter
    await websocket.accept()
    try:
        while True:
            # Receive JPEG bytes from frontend
            frame_bytes = await websocket.receive_bytes()
            frame_counter += 1
            
            # Process the frame (detect & annotate)
            annotated_bytes, roi = process_frame(frame_bytes)
            
            # Broadcast annotated frame to MJPEG stream clients
            await broadcast_frame(annotated_bytes)
            
            # Store ROI in database
            if roi:
                roi_data = schemas.RoiEventCreate(
                    frame_id=frame_counter,
                    x=roi['x'],
                    y=roi['y'],
                    w=roi['w'],
                    h=roi['h'],
                    confidence=roi['confidence']
                )
                await crud.create_roi_event(db, roi_data)
                
    except WebSocketDisconnect:
        print("WebSocket client disconnected")
    except Exception as e:
        print(f"Error in websocket loop: {e}")

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
async def get_roi_data(limit: int = 50, db: AsyncSession = Depends(database.get_db)):
    events = await crud.get_roi_events(db, limit=limit)
    return events
