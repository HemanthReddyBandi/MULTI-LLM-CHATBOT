import React, { useEffect, useState, useRef } from 'react';

const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:8000';

const WeatherPanel = ({ defaultCity = 'Hyderabad', refreshMs = 60000 }) => {
  const [city, setCity] = useState(defaultCity);
  const [units, setUnits] = useState('metric');
  const [current, setCurrent] = useState(null);
  const [forecast, setForecast] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const inputRef = useRef(null);

  const fetchData = async () => {
    try {
      setLoading(true); setError('');
      const res = await fetch(`${API_BASE_URL}/weather/combined?city=${encodeURIComponent(city)}&units=${units}`);
      if (!res.ok) throw new Error(await res.text());
      const data = await res.json();
      setCurrent(data.current);
      setForecast((data.forecast && data.forecast.list) || []);
    } catch (e) {
      const msg = typeof e === 'string' ? e : (e?.message || 'Failed to load weather');
      setError(msg);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
    const id = setInterval(fetchData, refreshMs);
    return () => clearInterval(id);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [city, units, refreshMs]);

  return (
    <div className="w-full max-w-5xl mx-auto p-6 space-y-8">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
        <h3 className="text-2xl font-semibold">Weather</h3>
        <div className="flex items-center gap-2">
          <input ref={inputRef} value={city} onChange={(e)=>setCity(e.target.value)} placeholder="Enter city" className="px-3 py-2 border rounded w-56" />
          <select value={units} onChange={(e)=>setUnits(e.target.value)} className="px-3 py-2 border rounded">
            <option value="metric">Metric °C</option>
            <option value="imperial">Imperial °F</option>
          </select>
          <button onClick={fetchData} className="px-3 py-2 bg-blue-600 text-white rounded hover:bg-blue-700">Refresh</button>
        </div>
      </div>

      <section className="grid md:grid-cols-3 gap-6">
        <div className="md:col-span-1 bg-white/80 backdrop-blur rounded-xl shadow p-6">
          <h4 className="text-xl font-semibold mb-3">Current</h4>
          {loading ? <div className="text-sm text-gray-500">Loading...</div> : error ? <div className="text-sm text-red-600">{error}</div> : current ? (
            <div>
              <div className="text-3xl font-bold">{Math.round(current.main.temp)}°{units === 'metric' ? 'C' : 'F'}</div>
              <div className="text-gray-700 mt-1">{current.weather?.[0]?.description}</div>
              <div className="text-sm text-gray-500 mt-2">{current.name}, {current.sys?.country}</div>
              <div className="mt-3 grid grid-cols-2 gap-2 text-sm">
                <div>Feels: {Math.round(current.main.feels_like)}°</div>
                <div>Humidity: {current.main.humidity}%</div>
                <div>Wind: {current.wind.speed} {units === 'metric' ? 'm/s' : 'mph'}</div>
                <div>Pressure: {current.main.pressure} hPa</div>
              </div>
            </div>
          ) : null}
        </div>
        <div className="md:col-span-2 bg-white/80 backdrop-blur rounded-xl shadow p-6">
          <h4 className="text-xl font-semibold mb-3">Forecast (next 24h)</h4>
          {loading ? <div className="text-sm text-gray-500">Loading...</div> : error ? <div className="text-sm text-red-600">{error}</div> : (
            <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-4">
              {forecast.slice(0, 8).map((it, i) => (
                <div key={i} className="p-4 rounded-lg border bg-white/80">
                  <div className="font-medium">{new Date(it.dt * 1000).toLocaleString()}</div>
                  <div className="text-2xl font-bold">{Math.round(it.main.temp)}°</div>
                  <div className="text-sm text-gray-600">{it.weather?.[0]?.description}</div>
                </div>
              ))}
            </div>
          )}
        </div>
      </section>
    </div>
  );
};

export default WeatherPanel;


