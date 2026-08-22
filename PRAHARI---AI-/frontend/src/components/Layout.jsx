import { NavLink, useLocation } from 'react-router-dom';
import { useEffect, useState } from 'react';
import { openAlertSocket, api } from '../lib/api';
import { timeAgo } from '../lib/format';

const NAV = [
  { to: '/', label: 'Command Center', icon: '🛰️', end: true },
  { to: '/scam', label: 'Digital Arrest Shield', icon: '📞' },
  { to: '/currency', label: 'Counterfeit Detection', icon: '💵' },
  { to: '/fraud', label: 'Fraud Network Graph', icon: '🕸️' },
  { to: '/geo', label: 'Geo Intelligence', icon: '🗺️' },
  { to: '/shield', label: 'Citizen Fraud Shield', icon: '🛡️' },
];

export default function Layout({ children }) {
  const [alerts, setAlerts] = useState([]);
  const [flash, setFlash] = useState(null);
  const [ai, setAi] = useState(null);
  const loc = useLocation();

  useEffect(() => {
    api.aiStatus().then(setAi).catch(() => setAi({ enabled: false }));
  }, []);

  useEffect(() => {
    const close = openAlertSocket((msg) => {
      if (msg.type === 'alert') {
        setAlerts((a) => [{ ...msg, ts: msg.ts || new Date().toISOString() }, ...a].slice(0, 40));
        setFlash(msg);
        setTimeout(() => setFlash(null), 6000);
      }
    });
    return close;
  }, []);

  return (
    <div className="min-h-screen flex bg-ink text-slate-200">
      {/* Sidebar */}
      <aside className="w-64 shrink-0 border-r border-edge bg-panel flex flex-col fixed h-screen">
        <div className="px-5 py-5 border-b border-edge">
          <div className="flex items-center gap-2.5">
            <span className="text-2xl">🛡️</span>
            <div>
              <div className="font-bold text-lg leading-none tracking-tight">
                <span className="text-saffron">Pra</span><span className="text-slate-100">ha</span><span className="text-india">ri</span>
              </div>
              <div className="text-[10px] uppercase tracking-widest text-slate-500 mt-1">Digital Public Safety</div>
            </div>
          </div>
        </div>
        <nav className="flex-1 p-3 space-y-1 overflow-y-auto">
          {NAV.map((n) => (
            <NavLink
              key={n.to}
              to={n.to}
              end={n.end}
              className={({ isActive }) =>
                `flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors ${
                  isActive ? 'bg-accent/15 text-accent border border-accent/30' : 'text-slate-400 hover:bg-panel2 hover:text-slate-200 border border-transparent'
                }`
              }
            >
              <span className="text-lg">{n.icon}</span>
              {n.label}
            </NavLink>
          ))}
        </nav>
        <div className="p-4 border-t border-edge text-[11px] text-slate-500 space-y-2">
          <div className="flex items-center gap-2">
            <span className="w-2 h-2 rounded-full bg-good animate-pulse" />
            Live feed connected
          </div>
          <div className="flex items-center gap-2" title={ai?.enabled ? `Gemini model: ${ai.model}` : 'Set GEMINI_API_KEY in backend/.env to enable'}>
            <span className={`w-2 h-2 rounded-full ${ai?.enabled ? 'bg-accent animate-pulse' : 'bg-slate-600'}`} />
            {ai?.enabled ? (
              <span>Gemini AI <span className="text-accent">online</span></span>
            ) : (
              <span>Gemini AI offline</span>
            )}
          </div>
          <div>National Cyber Helpline <span className="text-accent font-semibold">1930</span></div>
        </div>
      </aside>

      {/* Main */}
      <div className="flex-1 ml-64 flex flex-col min-h-screen">
        <TopBar location={loc.pathname} alertCount={alerts.length} />
        <main className="flex-1 p-6 max-w-[1400px] w-full mx-auto">{children}</main>
      </div>

      {/* Live alert ticker (right rail) */}
      <AlertRail alerts={alerts} />

      {flash && <FlashAlert data={flash} onClose={() => setFlash(null)} />}
    </div>
  );
}

function TopBar({ location, alertCount }) {
  const [now, setNow] = useState(new Date());
  useEffect(() => {
    const t = setInterval(() => setNow(new Date()), 1000);
    return () => clearInterval(t);
  }, []);
  return (
    <header className="h-14 border-b border-edge bg-panel/80 backdrop-blur sticky top-0 z-20 flex items-center justify-between px-6">
      <div className="text-sm text-slate-400">
        Live Threat Operations · <span className="text-slate-200">Multi-Agency Command Center</span>
      </div>
      <div className="flex items-center gap-4 text-sm">
        <span className="text-slate-500 font-mono tabular-nums">{now.toLocaleTimeString('en-IN')}</span>
        <span className="chip bg-danger/15 text-danger border border-danger/30">
          <span className="w-1.5 h-1.5 rounded-full bg-danger animate-pulse" /> {alertCount} live alerts
        </span>
      </div>
    </header>
  );
}

function AlertRail({ alerts }) {
  if (!alerts.length) return null;
  return (
    <div className="fixed bottom-4 right-4 w-80 space-y-2 z-30 max-h-[60vh] overflow-hidden pointer-events-none">
      {alerts.slice(0, 4).map((a, i) => (
        <div key={i} className="card p-3 border-l-4 border-l-danger bg-panel2 shadow-xl pointer-events-auto animate-[fadeIn_.3s]">
          <div className="flex items-center justify-between">
            <span className="chip bg-danger/15 text-danger text-[10px]">{(a.severity || 'high').toUpperCase()}</span>
            <span className="text-[10px] text-slate-500">{timeAgo(a.ts)}</span>
          </div>
          <p className="text-sm font-medium mt-1 text-slate-100">{a.title}</p>
          <p className="text-xs text-slate-400 mt-0.5 line-clamp-2">{a.body}</p>
        </div>
      ))}
    </div>
  );
}

function FlashAlert({ data, onClose }) {
  return (
    <div className="fixed top-16 left-1/2 -translate-x-1/2 z-50 pointer-events-auto">
      <div className="card px-5 py-3 border-danger/50 bg-panel2 shadow-2xl pulse-danger flex items-center gap-4">
        <span className="text-2xl">🚨</span>
        <div>
          <p className="font-semibold text-danger text-sm">{data.title}</p>
          <p className="text-xs text-slate-300">{data.body}</p>
        </div>
        <button onClick={onClose} className="text-slate-500 hover:text-slate-200 text-lg leading-none">×</button>
      </div>
    </div>
  );
}
