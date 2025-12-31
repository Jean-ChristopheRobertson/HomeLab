import { useState, useEffect } from 'react'

function App() {
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    const fetchData = async () => {
      try {
        // Get location
        let query = '';
        try {
          const pos = await new Promise((resolve, reject) => {
            navigator.geolocation.getCurrentPosition(resolve, reject, { timeout: 5000 });
          });
          query = `?lat=${pos.coords.latitude}&lon=${pos.coords.longitude}`;
        } catch (e) {
          console.log("Geolocation failed or denied, using default location.");
        }

        const response = await fetch(`/api/dashboard${query}`);
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        const result = await response.json();
        setData(result);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  if (loading) return <div className="loading">Loading dashboard data...</div>;
  if (error) return <div className="error">Error loading dashboard: {error}</div>;
  if (!data) return null;

  return (
    <div className="container">
      <h1>Homelab SRE Dashboard (React)</h1>
      <div className="grid">
        {/* Weather Card */}
        {data.weather && !data.weather.error ? (
          <div className="card">
            <h2>Weather: {data.weather.city}</h2>
            <div className="weather-temp">{data.weather.temperature}°{data.weather.unit}</div>
            <div>{data.weather.condition}</div>
          </div>
        ) : (
          <div className="card error"><h2>Weather</h2>Failed to load</div>
        )}

        {/* Hockey Card */}
        {data.hockey && !data.hockey.error ? (
          <div className="card">
            <h2>Hockey Scores</h2>
            {data.hockey.games && data.hockey.games.length > 0 ? (
              data.hockey.games.map((g, index) => (
                <div key={index} className="score-board">
                  <span>{g.home} vs {g.away}</span>
                  <span>{g.home_score} - {g.away_score} <small>({g.period})</small></span>
                </div>
              ))
            ) : (
              <div>No games today.</div>
            )}
          </div>
        ) : (
          <div className="card error"><h2>Hockey</h2>Failed to load</div>
        )}

        {/* News Card */}
        {data.news && !data.news.error ? (
          <div className="card">
            <h2>Local News</h2>
            {data.news.headlines.map((n, index) => (
              <div key={index} className="news-item">
                <div className="news-title">{n.title}</div>
                <div className="news-meta">{n.category} - {new Date(n.timestamp).toLocaleTimeString()}</div>
              </div>
            ))}
          </div>
        ) : (
          <div className="card error"><h2>News</h2>Failed to load</div>
        )}
      </div>
    </div>
  )
}

export default App
