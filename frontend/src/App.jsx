import { VideoFeed } from './components/VideoFeed';
import { RoiTable } from './components/RoiTable';

function App() {
  return (
    <div className="dashboard-container">
      <header>
        <h1>
          <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="var(--accent-color)" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <rect x="3" y="3" width="18" height="18" rx="2" ry="2" />
            <circle cx="8.5" cy="8.5" r="1.5" />
            <polyline points="21 15 16 10 5 21" />
          </svg>
          Mega AI Real-Time Face Detection
        </h1>
      </header>
      
      <main className="main-content">
        <section className="panel">
          <VideoFeed />
        </section>
        
        <section className="panel">
          <h2 className="panel-title">ROI Detection Log</h2>
          <RoiTable />
        </section>
      </main>
    </div>
  );
}

export default App;
