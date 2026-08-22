import { useEffect, useState } from 'react';
import { api } from '../lib/api';
import { pct, timeAgo, bandBg } from '../lib/format';
import { Card, Spinner, SectionTitle, Badge, Progress, Stat } from '../components/ui';

export default function Scam() {
  const [samples, setSamples] = useState([]);
  const [text, setText] = useState('');
  const [channel, setChannel] = useState('call');
  const [callerId, setCallerId] = useState('+91-98XXXX0001');
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [sessions, setSessions] = useState([]);
  const [stats, setStats] = useState(null);
  const [deep, setDeep] = useState(false);
  const [ai, setAi] = useState(null);

  const refresh = () => {
    api.scamSessions().then(setSessions).catch(() => {});
    api.scamStats().then(setStats).catch(() => {});
  };

  useEffect(() => {
    api.scamSamples().then(setSamples).catch(() => {});
    api.aiStatus().then(setAi).catch(() => setAi({ enabled: false }));
    refresh();
  }, []);

  async function analyze() {
    if (!text.trim()) return;
    setLoading(true);
    try {
      const r = await api.scamAnalyze({ transcript: text, channel, caller_id: callerId, persist: true, deep_analysis: deep });
      setResult(r);
      refresh();
    } catch (e) { console.error(e); }
    setLoading(false);
  }

  return (
    <div>
      <SectionTitle sub="Real-time NLP classifier trained on digital-arrest, courier, KYC and impersonation scripts. Flags active sessions to telecom providers & victims before financial transfer completes.">
        📞 Digital Arrest Scam Detection & Alerting
      </SectionTitle>

      {stats && (
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
          <Stat label="Sessions Analysed" value={stats.total_sessions} icon="📊" />
          <Stat label="High / Critical" value={stats.high_risk} accent="text-danger" icon="🚨" />
          <Stat label="Intercepted" value={stats.intercepted} accent="text-good" icon="🛑" />
          <Stat label="Digital-Arrest Type" value={stats.by_type?.digital_arrest || 0} accent="text-saffron" icon="⚖️" />
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
        {/* Analyzer console */}
        <Card title="Live Detection Console" subtitle="paste a call transcript / SMS / WhatsApp message">
          <div className="flex gap-2 mb-3 flex-wrap">
            {samples.map((s) => (
              <button key={s.label} onClick={() => { setText(s.text); setChannel(s.channel); }}
                className="chip bg-panel2 border border-edge text-slate-300 hover:border-accent hover:text-accent">
                {s.label}
              </button>
            ))}
          </div>
          <div className="flex gap-2 mb-3">
            <select value={channel} onChange={(e) => setChannel(e.target.value)}
              className="bg-panel2 border border-edge rounded-lg px-3 py-2 text-sm">
              <option value="call">📞 Call</option>
              <option value="sms">💬 SMS</option>
              <option value="whatsapp">🟢 WhatsApp</option>
            </select>
            <input value={callerId} onChange={(e) => setCallerId(e.target.value)}
              className="flex-1 bg-panel2 border border-edge rounded-lg px-3 py-2 text-sm font-mono" placeholder="Caller ID" />
          </div>
          <textarea value={text} onChange={(e) => setText(e.target.value)} rows={6}
            placeholder="e.g. This is Inspector Sharma from CBI. You are under digital arrest…"
            className="w-full bg-panel2 border border-edge rounded-lg px-3 py-2 text-sm resize-none focus:outline-none focus:border-accent" />
          <label className={`flex items-center gap-2 mt-3 text-xs select-none ${ai?.enabled ? 'text-slate-300 cursor-pointer' : 'text-slate-600 cursor-not-allowed'}`}
            title={ai?.enabled ? 'Adds a Gemini reasoning pass' : 'Set GEMINI_API_KEY in backend/.env to enable'}>
            <input type="checkbox" checked={deep} disabled={!ai?.enabled} onChange={(e) => setDeep(e.target.checked)} className="accent-accent" />
            ✦ Deep AI reasoning (Gemini) {ai?.enabled ? '' : '— offline'}
          </label>
          <button onClick={analyze} disabled={loading} className="btn btn-primary w-full mt-2">
            {loading ? 'Analysing…' : '⚡ Analyse Session'}
          </button>
        </Card>

        {/* Verdict */}
        <Card title="Classifier Verdict" subtitle="explainable, audit-ready output">
          {!result ? (
            <div className="text-center text-slate-500 py-12">
              <div className="text-5xl mb-3">🔍</div>
              Run a detection to see the AI verdict, risk score, and named indicators.
            </div>
          ) : (
            <div>
              <div className={`rounded-xl border p-4 mb-4 ${bandBg[result.risk_band]}`}>
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-xs uppercase tracking-wide opacity-80">Risk Band</p>
                    <p className="text-2xl font-bold capitalize">{result.risk_band}</p>
                  </div>
                  <div className="text-right">
                    <p className="text-xs uppercase tracking-wide opacity-80">Risk Score</p>
                    <p className="text-3xl font-bold tabular-nums">{pct(result.risk_score)}</p>
                  </div>
                </div>
                <p className="text-sm mt-2 font-medium">{result.scam_type_label}</p>
              </div>

              <div className="grid grid-cols-2 gap-3 mb-4 text-sm">
                <div className="bg-panel2 rounded-lg p-3 border border-edge">
                  <p className="text-xs text-slate-400 mb-1">ML model probability</p>
                  <Progress value={result.model_probability} tone="bg-accent" />
                  <p className="text-right text-xs mt-1 text-slate-300">{pct(result.model_probability)}</p>
                </div>
                <div className="bg-panel2 rounded-lg p-3 border border-edge">
                  <p className="text-xs text-slate-400 mb-1">Rule evidence</p>
                  <Progress value={result.rule_score} tone="bg-saffron" />
                  <p className="text-right text-xs mt-1 text-slate-300">{pct(result.rule_score)}</p>
                </div>
              </div>

              <p className="text-xs text-slate-400 mb-2">Detected indicators ({result.indicators.length})</p>
              <div className="space-y-1.5 mb-4 max-h-40 overflow-y-auto">
                {result.indicators.length === 0 && <p className="text-slate-500 text-sm">None — pattern looks genuine.</p>}
                {result.indicators.map((i, idx) => (
                  <div key={idx} className="flex items-start gap-2 text-sm bg-panel2 rounded-lg px-3 py-2 border border-edge">
                    <span className="text-danger">▸</span>
                    <div>
                      <span className="text-slate-200">{i.label}</span>
                      <span className="text-slate-500 font-mono text-xs ml-2">“{i.match}”</span>
                    </div>
                  </div>
                ))}
              </div>

              <div className="rounded-lg bg-accent/10 border border-accent/30 p-3">
                <p className="text-xs uppercase tracking-wide text-accent mb-1">⚡ Automated Action</p>
                <p className="text-sm text-slate-200">{result.recommended_action}</p>
              </div>

              {result.ai_analysis && (
                <div className="rounded-lg bg-panel2 border border-edge p-3 mt-3">
                  <p className="text-xs uppercase tracking-wide text-accent mb-1">✦ Gemini Analyst Reasoning</p>
                  <p className="text-sm text-slate-300 leading-relaxed">{result.ai_analysis}</p>
                </div>
              )}
            </div>
          )}
        </Card>
      </div>

      {/* Recent sessions */}
      <Card title="Recent Detection Sessions" subtitle="live database" right={<button onClick={refresh} className="text-xs text-accent hover:underline">Refresh</button>}>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="text-left text-slate-400 border-b border-edge">
                <th className="py-2 pr-4 font-medium">Time</th>
                <th className="py-2 pr-4 font-medium">Channel</th>
                <th className="py-2 pr-4 font-medium">Caller</th>
                <th className="py-2 pr-4 font-medium">Type</th>
                <th className="py-2 pr-4 font-medium">Risk</th>
                <th className="py-2 pr-4 font-medium">Status</th>
              </tr>
            </thead>
            <tbody>
              {sessions.slice(0, 12).map((s) => (
                <tr key={s.id} className="border-b border-edge/50 hover:bg-panel2">
                  <td className="py-2 pr-4 text-slate-400">{timeAgo(s.created_at)}</td>
                  <td className="py-2 pr-4 capitalize">{s.channel}</td>
                  <td className="py-2 pr-4 font-mono text-xs">{s.caller_id}</td>
                  <td className="py-2 pr-4 capitalize text-slate-300">{(s.scam_type || '').replace(/_/g, ' ')}</td>
                  <td className="py-2 pr-4">
                    <Badge className={bandBg[s.risk_band]}>{s.risk_band} {pct(s.risk_score)}</Badge>
                  </td>
                  <td className="py-2 pr-4 capitalize text-slate-400">{s.status}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Card>
    </div>
  );
}
