import React, { useEffect, useState } from 'react';

const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:8000';

const NewsPanel = ({ country = 'in', category = null, refreshMs = 60000 }) => {
  const [headlines, setHeadlines] = useState([]);
  const [sources, setSources] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [query, setQuery] = useState('');
  const [stocks, setStocks] = useState([]);

  const fetchData = async () => {
    try {
      setLoading(true);
      setError('');
      const qs = new URLSearchParams();
      if (country) qs.set('country', country);
      if (category) qs.set('category', category);
      if (query) qs.set('q', query);
      const res = await fetch(`${API_BASE_URL}/news/combined?${qs.toString()}`);
      const data = await res.json();
      const h = data.headlines?.articles || [];
      const s = data.sources?.sources || [];
      setHeadlines(h);
      setSources(s);
      const stocksRes = await fetch(`${API_BASE_URL}/news/stocks?limit=15`);
      const stocksData = await stocksRes.json();
      setStocks(stocksData.items || []);
    } catch (e) {
      setError('Failed to load news');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
    const id = setInterval(fetchData, refreshMs);
    return () => clearInterval(id);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [country, category, refreshMs, query]);

  return (
    <div className="w-full max-w-6xl mx-auto p-6 space-y-10">
      {/* Controls */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
        <h3 className="text-2xl font-semibold">News & Markets</h3>
        <div className="flex items-center gap-2">
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Search topics (e.g., AI, markets)"
            className="px-3 py-2 border rounded w-64"
          />
          <button onClick={fetchData} className="px-3 py-2 bg-blue-600 text-white rounded hover:bg-blue-700">Refresh</button>
          <button
            onClick={async () => {
              try { await navigator.mediaDevices.getUserMedia({ audio: true }); } catch { alert('Microphone access denied.'); return; }
              if (!('webkitSpeechRecognition' in window)) { alert('Voice recognition not supported.'); return; }
              const rec = new window.webkitSpeechRecognition();
              rec.lang = 'en-US'; rec.interimResults = false; rec.maxAlternatives = 1;
              rec.onresult = (e) => setQuery(e.results[0][0].transcript);
              rec.start();
            }}
            className="px-3 py-2 bg-gray-200 text-gray-800 rounded hover:bg-gray-300"
            title="Voice search"
          >🎤</button>
        </div>
      </div>

      {/* Headlines grid */}
      <section className="bg-white/80 backdrop-blur rounded-xl shadow p-6">
        <h4 className="text-xl font-semibold mb-4">Top Headlines</h4>
        {loading ? (
          <div className="text-sm text-gray-500">Loading...</div>
        ) : error ? (
          <div className="text-sm text-red-600">{error}</div>
        ) : (
          <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-6">
            {headlines.slice(0, 12).map((a, i) => (
              <article key={i} className="rounded-lg border bg-white/80 hover:shadow transition">
                <a href={a.url} target="_blank" rel="noreferrer">
                  {a.urlToImage ? (
                    <img src={a.urlToImage} alt="cover" className="w-full h-40 object-cover rounded-t-lg" />
                  ) : (
                    <div className="w-full h-40 bg-gray-200 rounded-t-lg" />
                  )}
                </a>
                <div className="p-4">
                  <a href={a.url} target="_blank" rel="noreferrer" className="font-medium text-blue-700 hover:underline line-clamp-3">{a.title || 'Untitled'}</a>
                  <div className="text-xs text-gray-500 mt-1">{(a.source && a.source.name) || ''}</div>
                  {a.description && <div className="text-sm text-gray-700 mt-2 line-clamp-3">{a.description}</div>}
                </div>
              </article>
            ))}
          </div>
        )}
      </section>

      {/* Sources and Stocks */}
      <section className="grid md:grid-cols-2 gap-8">
        <div className="bg-white/80 backdrop-blur rounded-xl shadow p-6">
          <h4 className="text-xl font-semibold mb-4">Sources</h4>
          <ul className="space-y-3 max-h-[60vh] overflow-auto">
            {sources.slice(0, 40).map((s, i) => (
              <li key={i} className="text-sm text-gray-800">
                <a className="text-blue-700 hover:underline" href={s.url} target="_blank" rel="noreferrer">{s.name}</a>
                {s.category && <span className="ml-2 text-xs text-gray-500">({s.category})</span>}
              </li>
            ))}
          </ul>
        </div>
        <div className="bg-white/80 backdrop-blur rounded-xl shadow p-6">
          <h4 className="text-xl font-semibold mb-4">Stock / Market News</h4>
          <ul className="space-y-3 max-h-[60vh] overflow-auto">
            {stocks.map((item, i) => (
              <li key={i} className="text-sm">
                <a className="text-blue-700 hover:underline" href={item.link} target="_blank" rel="noreferrer">{item.title}</a>
                {item.published && <div className="text-xs text-gray-500">{item.published}</div>}
              </li>
            ))}
          </ul>
        </div>
      </section>
    </div>
  );
};

export default NewsPanel;


