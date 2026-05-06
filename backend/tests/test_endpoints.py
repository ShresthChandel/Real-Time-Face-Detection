import pytest
from fastapi.testclient import TestClient
from app.main import app
from app import database

client = TestClient(app)

def test_get_roi_data_endpoint():
    # Test that the REST endpoint returns a valid 200 response
    # We use a mocked database dependency to avoid needing a live Postgres instance for CI tests
    
    # Simple mock response
    async def mock_get_db():
        yield None
        
    app.dependency_overrides[database.get_db] = mock_get_db
    
    # Since we can't easily mock the DB session perfectly without a real async session,
    # and the endpoint calls crud.get_roi_events, we'll patch crud directly
    import app.crud as crud
    
    async def mock_get_roi_events(*args, **kwargs):
        return []
        
    # Apply monkeypatch (using standard python mocking for simplicity in this file)
    original_get_roi_events = crud.get_roi_events
    crud.get_roi_events = mock_get_roi_events
    
    try:
        response = client.get("/roi-data")
        assert response.status_code == 200
        assert response.json() == []
    finally:
        # Cleanup
        crud.get_roi_events = original_get_roi_events
        app.dependency_overrides.clear()

def test_websocket_endpoint():
    # Test that the websocket accepts connections and can process a real frame
    import io
    import asyncio
    from PIL import Image
    import app.main as main_module
    
    with client.websocket_connect("/ws/video-feed") as websocket:
        # Create a tiny 1x1 white JPEG image
        buf = io.BytesIO()
        Image.new("RGB", (10, 10), "white").save(buf, format="JPEG")
        frame_bytes = buf.getvalue()
        
        # Add a test subscriber to verify broadcasting
        q = asyncio.Queue(maxsize=2)
        main_module.subscribers.add(q)
        
        try:
            # Send the valid JPEG bytes
            websocket.send_bytes(frame_bytes)
            
            # Verify the queue received a frame (meaning process_frame and broadcast_frame succeeded)
            # TestClient handles async execution, but we'll just check if it's not empty
            # If not empty immediately, it means broadcast worked.
            assert not q.empty()
        finally:
            main_module.subscribers.remove(q)
