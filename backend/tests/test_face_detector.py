import pytest
from PIL import Image
from app.face_detector import detector

def test_face_detector_no_face():
    # Create a completely blank black image (no face)
    img = Image.new('RGB', (640, 480), color='black')
    
    # Process it
    result = detector.detect(img)
    
    # The detector should correctly return None when no face is found
    assert result is None
