import mediapipe as mp
import numpy as np
from PIL import Image

class FaceDetector:
    def __init__(self, min_detection_confidence=0.5):
        self.mp_face_detection = mp.solutions.face_detection
        self.detector = self.mp_face_detection.FaceDetection(
            model_selection=0, # 0 for short-range (<2m)
            min_detection_confidence=min_detection_confidence
        )

    def detect(self, image: Image.Image):
        """
        Detects a face in a PIL image.
        Returns a dict {x, y, w, h, confidence} in pixel coordinates, or None.
        """
        # Convert PIL Image to numpy array (RGB)
        image_np = np.array(image.convert("RGB"))
        
        # Process the image
        results = self.detector.process(image_np)
        
        if not results.detections:
            return None
            
        # We assume only one face as per requirements
        detection = results.detections[0]
        bboxC = detection.location_data.relative_bounding_box
        
        img_width, img_height = image.size
        
        # Convert normalized coordinates to pixel coordinates
        x = int(bboxC.xmin * img_width)
        y = int(bboxC.ymin * img_height)
        w = int(bboxC.width * img_width)
        h = int(bboxC.height * img_height)
        
        # Ensure coordinates are within image boundaries
        x = max(0, x)
        y = max(0, y)
        w = min(w, img_width - x)
        h = min(h, img_height - y)
        
        confidence = detection.score[0] if detection.score else 0.0
        
        return {
            "x": x,
            "y": y,
            "w": w,
            "h": h,
            "confidence": float(confidence)
        }

# Singleton instance
detector = FaceDetector()
