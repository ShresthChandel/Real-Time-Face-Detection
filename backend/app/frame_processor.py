import io
from PIL import Image, ImageDraw
from .face_detector import detector

def process_frame(frame_bytes: bytes):
    """
    Decodes bytes -> PIL Image -> detects face -> draws rectangle -> re-encodes to JPEG bytes.
    Returns (annotated_jpeg_bytes, roi_dict or None)
    """
    try:
        # Decode bytes to PIL Image
        image = Image.open(io.BytesIO(frame_bytes))
        
        # Detect face
        roi = detector.detect(image)
        
        # Annotate image if face found
        if roi:
            draw = ImageDraw.Draw(image)
            x, y, w, h = roi['x'], roi['y'], roi['w'], roi['h']
            draw.rectangle(
                [x, y, x + w, y + h],
                outline="lime",
                width=3
            )
            
        # Re-encode to JPEG
        output_buffer = io.BytesIO()
        image.save(output_buffer, format="JPEG")
        annotated_bytes = output_buffer.getvalue()
        
        return annotated_bytes, roi
        
    except Exception as e:
        # If any error occurs (e.g., bad image bytes), return original bytes and no ROI
        print(f"Error processing frame: {e}")
        return frame_bytes, None
