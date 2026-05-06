import { useState, useEffect, useRef, useCallback } from 'react';

const WEBSOCKET_URL = import.meta.env.VITE_WS_URL || 'ws://localhost:8000/ws/video-feed';

export function useWebSocket(videoRef, canvasRef) {
  const [isConnected, setIsConnected] = useState(false);
  const wsRef = useRef(null);
  const frameIntervalRef = useRef(null);

  const connect = useCallback(() => {
    wsRef.current = new WebSocket(WEBSOCKET_URL);

    wsRef.current.onopen = () => {
      console.log('WebSocket connected');
      setIsConnected(true);
    };

    wsRef.current.onclose = () => {
      console.log('WebSocket disconnected');
      setIsConnected(false);
      // Attempt to reconnect after 2 seconds
      setTimeout(connect, 2000);
    };

    wsRef.current.onerror = (error) => {
      console.error('WebSocket error:', error);
      wsRef.current.close();
    };
  }, []);

  useEffect(() => {
    connect();
    return () => {
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, [connect]);

  // Capture and send frames
  useEffect(() => {
    if (!isConnected || !videoRef.current || !canvasRef.current) return;

    const sendFrame = () => {
      const video = videoRef.current;
      const canvas = canvasRef.current;
      
      if (video.readyState === video.HAVE_ENOUGH_DATA && wsRef.current?.readyState === WebSocket.OPEN) {
        // Set canvas dimensions to match video
        canvas.width = video.videoWidth;
        canvas.height = video.videoHeight;
        
        const ctx = canvas.getContext('2d');
        ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
        
        // Extract JPEG blob
        canvas.toBlob((blob) => {
          if (blob) {
            wsRef.current.send(blob);
          }
        }, 'image/jpeg', 0.7); // 70% quality to save bandwidth
      }
    };

    // ~10 fps
    frameIntervalRef.current = setInterval(sendFrame, 100);

    return () => {
      if (frameIntervalRef.current) {
        clearInterval(frameIntervalRef.current);
      }
    };
  }, [isConnected, videoRef, canvasRef]);

  return { isConnected };
}
