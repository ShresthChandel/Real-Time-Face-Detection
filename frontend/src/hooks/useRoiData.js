import { useState, useEffect, useRef } from 'react';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export function useRoiData() {
  const [roiData, setRoiData] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await fetch(`${API_URL}/roi-data?limit=50`);
        if (!response.ok) {
          throw new Error('Network response was not ok');
        }
        const data = await response.json();
        setRoiData(data);
        setError(null);
      } catch (err) {
        console.error("Error fetching ROI data:", err);
        setError(err.message);
      } finally {
        setIsLoading(false);
      }
    };

    // Initial fetch
    fetchData();

    // Poll every 1 second
    const interval = setInterval(() => {
      if (!document.hidden) {
        fetchData();
      }
    }, 1000);

    return () => clearInterval(interval);
  }, []);

  return { roiData, isLoading, error };
}
