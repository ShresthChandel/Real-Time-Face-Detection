import { useRef, useEffect } from 'react';
import { useWebSocket } from '../hooks/useWebSocket';

const STREAM_URL = import.meta.env.VITE_STREAM_URL || 'http://localhost:8000/stream';

export function VideoFeed() {
  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  
  const { isConnected } = useWebSocket(videoRef, canvasRef);

  // Initialize webcam
  useEffect(() => {
    const startWebcam = async () => {
      try {
        const stream = await navigator.mediaDevices.getUserMedia({ 
          video: { width: 640, height: 480, frameRate: { ideal: 10, max: 15 } } 
        });
        if (videoRef.current) {
          videoRef.current.srcObject = stream;
        }
      } catch (err) {
        console.error("Error accessing webcam:", err);
      }
    };

    startWebcam();

    return () => {
      if (videoRef.current && videoRef.current.srcObject) {
        videoRef.current.srcObject.getTracks().forEach(track => track.stop());
      }
    };
  }, []);

  return (
    <div className="video-container">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.5rem' }}>
        <h2 className="panel-title">Annotated Stream</h2>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', fontSize: '0.8rem', color: 'var(--text-secondary)' }}>
          <div className={`status-indicator ${isConnected ? 'connected' : ''}`} />
          {isConnected ? 'WS Connected' : 'WS Disconnected'}
        </div>
      </div>
      
      {/* Annotated stream from backend */}
      <div className="video-wrapper">
        <img src={STREAM_URL} alt="Annotated Video Stream" className="annotated-stream" />
      </div>

      <h2 className="panel-title" style={{ marginTop: '1rem' }}>Raw Webcam Feed</h2>
      {/* Raw webcam feed (small preview) */}
      <div className="video-wrapper" style={{ height: '150px', border: '1px solid rgba(255,255,255,0.1)' }}>
        <video 
          ref={videoRef} 
          autoPlay 
          playsInline 
          muted 
        />
      </div>

      {/* Hidden canvas for extracting frames */}
      <canvas ref={canvasRef} className="hidden-canvas" />
    </div>
  );
}
