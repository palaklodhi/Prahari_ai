// API client — talks to the FastAPI backend via the Vite proxy (/api).
const BASE = import.meta.env.VITE_API_BASE || '';

async function req(path, opts = {}) {
  const res = await fetch(BASE + path, {
    headers: { 'Content-Type': 'application/json', ...(opts.headers || {}) },
    ...opts,
  });
  if (!res.ok) throw new Error(`${res.status} ${res.statusText}`);
  return res.json();
}

export const api = {
  health: () => req('/api/health'),
  overview: () => req('/api/dashboard/overview'),
  feed: () => req('/api/dashboard/feed'),

  // scam
  scamSamples: () => req('/api/scam/samples'),
  scamAnalyze: (body) => req('/api/scam/analyze', { method: 'POST', body: JSON.stringify(body) }),
  scamSessions: () => req('/api/scam/sessions'),
  scamStats: () => req('/api/scam/stats'),

  // currency
  denominations: () => req('/api/currency/denominations'),
  currencyScans: () => req('/api/currency/scans'),
  currencyStats: () => req('/api/currency/stats'),
  currencyScan: (formData) =>
    fetch(BASE + '/api/currency/scan', { method: 'POST', body: formData }).then((r) => {
      if (!r.ok) throw new Error('scan failed');
      return r.json();
    }),

  // fraud
  fraudNetwork: () => req('/api/fraud/network'),
  fraudRings: () => req('/api/fraud/rings'),
  intelPackage: (id) => req(`/api/fraud/intelligence-package/${id}`),

  // geo
  hotspots: () => req('/api/geo/hotspots'),
  incidents: (cat) => req('/api/geo/incidents' + (cat ? `?category=${cat}` : '')),

  // shield
  shieldLanguages: () => req('/api/shield/languages'),
  shieldAssess: (body) => req('/api/shield/assess', { method: 'POST', body: JSON.stringify(body) }),

  // ai (Gemini augmentation)
  aiStatus: () => req('/api/ai/status'),
  aiAsk: (body) => req('/api/ai/ask', { method: 'POST', body: JSON.stringify(body) }),
};

export function openAlertSocket(onMessage) {
  const proto = location.protocol === 'https:' ? 'wss' : 'ws';
  const url = `${proto}://${location.host}/ws/alerts`;
  let ws;
  let closed = false;
  function connect() {
    ws = new WebSocket(url);
    ws.onmessage = (e) => {
      try { onMessage(JSON.parse(e.data)); } catch {}
    };
    ws.onclose = () => { if (!closed) setTimeout(connect, 2500); };
    ws.onerror = () => ws.close();
  }
  connect();
  return () => { closed = true; ws && ws.close(); };
}
