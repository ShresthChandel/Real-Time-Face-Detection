import { useRoiData } from '../hooks/useRoiData';

export function RoiTable() {
  const { roiData, isLoading, error } = useRoiData();

  if (isLoading && roiData.length === 0) {
    return <div style={{ padding: '1rem', color: 'var(--text-secondary)' }}>Loading ROI data...</div>;
  }

  if (error) {
    return <div style={{ padding: '1rem', color: '#ef4444' }}>Error: {error}</div>;
  }

  if (roiData.length === 0) {
    return <div style={{ padding: '1rem', color: 'var(--text-secondary)' }}>No face detections recorded yet.</div>;
  }

  return (
    <div className="table-container">
      <table>
        <thead>
          <tr>
            <th>Frame ID</th>
            <th>Bounding Box (x, y, w, h)</th>
            <th>Confidence</th>
            <th>Time</th>
          </tr>
        </thead>
        <tbody>
          {roiData.map((row) => (
            <tr key={row.id}>
              <td>{row.frame_id}</td>
              <td>[{row.x}, {row.y}, {row.w}, {row.h}]</td>
              <td>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <div className="confidence-bar">
                    <div 
                      className="confidence-level" 
                      style={{ width: `${(row.confidence * 100).toFixed(0)}%` }} 
                    />
                  </div>
                  <span>{(row.confidence * 100).toFixed(1)}%</span>
                </div>
              </td>
              <td>{new Date(row.created_at).toLocaleTimeString()}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
