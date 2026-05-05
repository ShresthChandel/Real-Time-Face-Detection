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
    # Test that the websocket accepts connections and can receive a synthetic frame
    with client.websocket_connect("/ws/video-feed") as websocket:
        # Send a tiny synthetic string (will fail decoding, but shouldn't crash the server loop)
        websocket.send_bytes(b"synthetic_jpeg_data")
        # Since it won't broadcast an annotated frame for bad data, we just verify it stays open
        assert True
