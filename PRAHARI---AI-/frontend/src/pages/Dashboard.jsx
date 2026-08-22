import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import {
  AreaChart, Area, ResponsiveContainer, XAxis, YAxis, Tooltip, CartesianGrid,
  PieChart, Pie, Cell, BarChart, Bar,
} from 'recharts';
import { api } from '../lib/api';
import { inr, num, timeAgo } from '../lib/format';
import { Card, Stat, Spinner, SectionTitle, Badge } from '../components/ui';

const PIE = ['#38bdf8', '#ff9933', '#f43f5e', '#34d399', '#a78bfa', '#fbbf24'];

export default function Dashboard() {
  const [data, setData] = useState(null);
  const [feed, setFeed] = useState([]);

  useEffect(() => {
    api.overview().then(setData).catch(console.error);
    api.feed().then(setFeed).catch(console.error);
    const t = setInterval(() => api.feed().then(setFeed).catch(() => {}), 8000);
    return () => clearInterval(t);
  }, []);

  if (!data) return <Spinner label="Loading command center…" />;
  const k = data.kpis;

  const typeData = Object.entries(data.scam_by_type || {}).map(([name, value]) => ({
    name: name.replace(/_/g, ' '), value,
  }));
  const catData = Object.entries(data.incidents_by_category || {}).map(([name, value]) => ({
    name: name.replace(/_/g, ' '), value,
  }));

  return (
    <div>
      <SectionTitle sub="Real-time multi-source intelligence fusion across all threat vectors — shifting from reactive investigation to predictive neutralisation.">
        🛰️ National Command Center
      </SectionTitle>

      {/* KPI row */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
        <Stat label="High-Risk Scam Sessions" value={num(k.high_risk_scams)} sub={`${num(k.scam_sessions)} total analysed`} accent="text-danger" icon="📞" />
        <Stat label="Sessions Intercepted" value={num(k.sessions_intercepted)} sub="before financial loss" accent="text-good" icon="🛑" />
        <Stat label="Counterfeit Detected" value={num(k.counterfeit_detected)} sub={`${num(k.currency_scans)} notes scanned`} accent="text-warn" icon="💵" />
        <Stat label="Fraud Rings Mapped" value={num(k.fraud_rings)} sub={`${num(k.accounts_in_rings)} accounts linked`} accent="text-accent" icon="🕸️" />
        <Stat label="Network Flow Traced" value={inr(k.network_flow)} sub="across mule chains" accent="text-accent" icon="💸" />
        <Stat label="Crime Incidents" value={num(k.crime_incidents)} sub={`${num(k.critical_hotspots)} critical hotspots`} accent="text-saffron" icon="📍" />
        <Stat label="Reported Losses" value={inr(k.total_loss)} sub="cumulative, all vectors" accent="text-danger" icon="⚠️" />
        <Stat label="Estimated Prevented" value={inr(k.sessions_intercepted * 480000)} sub="from interceptions" accent="text-good" icon="✅" />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-6">
        {/* Trend */}
        <Card title="Scam Session Trend" subtitle="14-day detection volume" className="lg:col-span-2">
          <ResponsiveContainer width="100%" height={240}>
            <AreaChart data={data.scam_trend}>
              <defs>
                <linearGradient id="g1" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stopColor="#38bdf8" stopOpacity={0.5} />
                  <stop offset="100%" stopColor="#38bdf8" stopOpacity={0} />
                </linearGradient>
                <linearGradient id="g2" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stopColor="#f43f5e" stopOpacity={0.5} />
                  <stop offset="100%" stopColor="#f43f5e" stopOpacity={0} />
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="#1f2942" />
              <XAxis dataKey="date" tick={{ fill: '#64748b', fontSize: 11 }} tickFormatter={(d) => d.slice(5)} />
              <YAxis tick={{ fill: '#64748b', fontSize: 11 }} allowDecimals={false} />
              <Tooltip contentStyle={{ background: '#161d30', border: '1px solid #1f2942', borderRadius: 8 }} />
              <Area type="monotone" dataKey="sessions" stroke="#38bdf8" fill="url(#g1)" strokeWidth={2} name="All sessions" />
              <Area type="monotone" dataKey="high_risk" stroke="#f43f5e" fill="url(#g2)" strokeWidth={2} name="High-risk" />
            </AreaChart>
          </ResponsiveContainer>
        </Card>

        {/* Scam type breakdown */}
        <Card title="Scam Type Distribution" subtitle="detected categories">
          <ResponsiveContainer width="100%" height={240}>
            <PieChart>
              <Pie data={typeData} dataKey="value" nameKey="name" innerRadius={45} outerRadius={80} paddingAngle={3}>
                {typeData.map((_, i) => <Cell key={i} fill={PIE[i % PIE.length]} />)}
              </Pie>
              <Tooltip contentStyle={{ background: '#161d30', border: '1px solid #1f2942', borderRadius: 8 }} />
            </PieChart>
          </ResponsiveContainer>
          <div className="flex flex-wrap gap-2 mt-2">
            {typeData.map((t, i) => (
              <span key={t.name} className="chip bg-panel2 text-slate-300 text-[11px]">
                <span className="w-2 h-2 rounded-full" style={{ background: PIE[i % PIE.length] }} /> {t.name}
              </span>
            ))}
          </div>
        </Card>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Live intelligence feed */}
        <Card title="Live Intelligence Feed" subtitle="cross-module alerts" className="lg:col-span-1">
          <div className="space-y-2 max-h-[360px] overflow-y-auto pr-1">
            {feed.length === 0 && <p className="text-slate-500 text-sm">No alerts yet.</p>}
            {feed.map((a) => (
              <div key={a.id} className="p-3 rounded-lg bg-panel2 border border-edge">
                <div className="flex items-center justify-between mb-1">
                  <Badge className={sevBg(a.severity)}>{a.kind}</Badge>
                  <span className="text-[10px] text-slate-500">{timeAgo(a.created_at)}</span>
                </div>
                <p className="text-sm font-medium text-slate-100">{a.title}</p>
                <p className="text-xs text-slate-400 mt-0.5">{a.body}</p>
              </div>
            ))}
          </div>
        </Card>

        {/* Top hotspots */}
        <Card title="Priority Hotspots" subtitle="geospatial clusters" right={<Link to="/geo" className="text-xs text-accent hover:underline">Open map →</Link>}>
          <div className="space-y-3">
            {data.top_hotspots.map((h) => (
              <div key={h.id} className="flex items-center gap-3">
                <span className={`w-2.5 h-2.5 rounded-full ${h.priority === 'critical' ? 'bg-danger' : h.priority === 'high' ? 'bg-warn' : 'bg-accent'}`} />
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium text-slate-100 truncate">{h.city}, {h.state}</p>
                  <p className="text-xs text-slate-500">{h.incident_count} incidents · {h.dominant_category.replace(/_/g, ' ')}</p>
                </div>
                <span className="text-xs text-danger font-semibold">{inr(h.total_loss)}</span>
              </div>
            ))}
          </div>
        </Card>

        {/* Top fraud rings */}
        <Card title="Active Fraud Rings" subtitle="graph intelligence" right={<Link to="/fraud" className="text-xs text-accent hover:underline">Investigate →</Link>}>
          <div className="space-y-3">
            {data.top_rings.map((r) => (
              <div key={r.ring_id} className="p-3 rounded-lg bg-panel2 border border-edge">
                <div className="flex items-center justify-between">
                  <span className="font-semibold text-slate-100">Ring #{r.ring_id}</span>
                  <Badge className="bg-danger/15 text-danger border-danger/30">risk {Math.round(r.risk * 100)}%</Badge>
                </div>
                <p className="text-xs text-slate-400 mt-1">
                  {r.size} accounts · {inr(r.total_flow)} · {r.kingpins.length} kingpin, {r.mules.length} mules
                </p>
              </div>
            ))}
          </div>
        </Card>
      </div>
    </div>
  );
}

function sevBg(s) {
  return {
    critical: 'bg-danger/15 text-danger border-danger/30',
    high: 'bg-warn/15 text-warn border-warn/30',
    info: 'bg-accent/15 text-accent border-accent/30',
  }[s] || 'bg-panel2 text-slate-300 border-edge';
}
