import { useEffect, useRef, useState } from 'react';
import { api } from '../lib/api';
import { pct, timeAgo, verdictBg } from '../lib/format';
import { Card, Spinner, SectionTitle, Badge, Progress, Stat } from '../components/ui';

export default function Currency() {
  const [denoms, setDenoms] = useState([]);
  const [denom, setDenom] = useState(500);
  const [serial, setSerial] = useState('');
  const [file, setFile] = useState(null);
  const [preview, setPreview] = useState(null);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [scans, setScans] = useState([]);
  const [stats, setStats] = useState(null);
  const inputRef = useRef();

  const refresh = () => {
    api.currencyScans().then(setScans).catch(() => {});
    api.currencyStats().then(setStats).catch(() => {});
  };

  useEffect(() => {
    api.denominations().then(setDenoms).catch(() => {});
    refresh();
  }, []);

  function onFile(f) {
    if (!f) return;
    setFile(f);
    setPreview(URL.createObjectURL(f));
    setResult(null);
  }

  async function scan() {
    if (!file) return;
    setLoading(true);
    const fd = new FormData();
    fd.append('denomination', denom);
    if (serial) fd.append('serial', serial);
    fd.append('operator', 'Field Officer');
    fd.append('location', 'Command Center');
    fd.append('file', file);
    try {
      const r = await api.currencyScan(fd);
      setResult(r);
      refresh();
    } catch (e) { console.error(e); }
    setLoading(false);
  }

  return (
    <div>
      <SectionTitle sub="Computer-vision agent deployable on phones, bank counting machines & PoS terminals. Micro-print, security-thread, colour & serial validation across all denominations.">
        💵 Counterfeit Currency Identification Agent
      </SectionTitle>

      {stats && (
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
          <Stat label="Notes Scanned" value={stats.total_scans} icon="🔎" />
          <Stat label="Counterfeit Found" value={stats.counterfeit} accent="text-danger" icon="🚫" />
          <Stat label="Flagged Suspect" value={stats.suspect} accent="text-warn" icon="⚠️" />
          <Stat label="Detection Rate" value={pct(stats.detection_rate)} accent="text-accent" icon="🎯" />
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
        <Card title="Scan a Note" subtitle="upload an image capture">
          <div className="flex gap-2 mb-3 flex-wrap">
            {denoms.map((d) => (
              <button key={d.denomination} onClick={() => setDenom(d.denomination)}
                className={`chip border ${denom === d.denomination ? 'bg-accent/15 text-accent border-accent/40' : 'bg-panel2 border-edge text-slate-300'}`}>
                ₹{d.denomination}
              </button>
            ))}
          </div>

          <div
            onClick={() => inputRef.current?.click()}
            onDragOver={(e) => e.preventDefault()}
            onDrop={(e) => { e.preventDefault(); onFile(e.dataTransfer.files[0]); }}
            className="border-2 border-dashed border-edge rounded-xl h-48 flex items-center justify-center cursor-pointer hover:border-accent overflow-hidden bg-panel2">
            {preview ? (
              <img src={preview} alt="note" className="max-h-full max-w-full object-contain" />
            ) : (
              <div className="text-center text-slate-500">
                <div className="text-4xl mb-2">🖼️</div>
                Click or drop a note image
              </div>
            )}
          </div>
          <input ref={inputRef} type="file" accept="image/*" className="hidden" onChange={(e) => onFile(e.target.files[0])} />

          <input value={serial} onChange={(e) => setSerial(e.target.value)} placeholder="Serial (e.g. 8AB 123456) — optional"
            className="w-full bg-panel2 border border-edge rounded-lg px-3 py-2 text-sm font-mono mt-3" />

          <button onClick={scan} disabled={loading || !file} className="btn btn-primary w-full mt-3 disabled:opacity-40">
            {loading ? 'Analysing features…' : '🔬 Verify Authenticity'}
          </button>
          <p className="text-[11px] text-slate-500 mt-2">
            Tip: any note/document image works for the demo — the pipeline extracts real aspect-ratio, colour, micro-print (high-frequency), security-thread & sharpness features.
          </p>
        </Card>

        <Card title="Authenticity Report" subtitle="per-feature breakdown">
          {!result ? (
            <div className="text-center text-slate-500 py-16">
              <div className="text-5xl mb-3">🧾</div>
              Upload and verify a note to see the security-feature analysis.
            </div>
          ) : (
            <div>
              <div className={`rounded-xl border p-4 mb-4 ${verdictBg[result.verdict]}`}>
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-xs uppercase tracking-wide opacity-80">Verdict · ₹{result.denomination}</p>
                    <p className="text-2xl font-bold capitalize">{result.verdict}</p>
                  </div>
                  <div className="text-right">
                    <p className="text-xs uppercase tracking-wide opacity-80">Authenticity</p>
                    <p className="text-3xl font-bold tabular-nums">{pct(result.authenticity_score)}</p>
                  </div>
                </div>
              </div>

              <div className="space-y-2 mb-4">
                {result.checks.map((c, i) => (
                  <div key={i} className="bg-panel2 rounded-lg p-3 border border-edge">
                    <div className="flex items-center justify-between mb-1">
                      <span className="text-sm text-slate-200 flex items-center gap-2">
                        {c.passed ? <span className="text-good">✓</span> : <span className="text-danger">✕</span>}
                        {c.name}
                      </span>
                      <span className="text-xs text-slate-400 tabular-nums">{pct(c.score)}</span>
                    </div>
                    <Progress value={c.score} tone={c.passed ? 'bg-good' : 'bg-danger'} />
                    <p className="text-[11px] text-slate-500 mt-1">{c.detail}</p>
                  </div>
                ))}
              </div>

              <div className="rounded-lg bg-accent/10 border border-accent/30 p-3">
                <p className="text-xs uppercase tracking-wide text-accent mb-1">Field Recommendation</p>
                <p className="text-sm text-slate-200">{result.recommendation}</p>
              </div>
            </div>
          )}
        </Card>
      </div>

      <Card title="Recent Scans" subtitle="field & teller activity">
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="text-left text-slate-400 border-b border-edge">
                <th className="py-2 pr-4 font-medium">Time</th>
                <th className="py-2 pr-4 font-medium">Denom</th>
                <th className="py-2 pr-4 font-medium">Verdict</th>
                <th className="py-2 pr-4 font-medium">Score</th>
                <th className="py-2 pr-4 font-medium">Serial</th>
                <th className="py-2 pr-4 font-medium">Operator</th>
              </tr>
            </thead>
            <tbody>
              {scans.slice(0, 12).map((s) => (
                <tr key={s.id} className="border-b border-edge/50 hover:bg-panel2">
                  <td className="py-2 pr-4 text-slate-400">{timeAgo(s.created_at)}</td>
                  <td className="py-2 pr-4">₹{s.denomination}</td>
                  <td className="py-2 pr-4"><Badge className={verdictBg[s.verdict]}>{s.verdict}</Badge></td>
                  <td className="py-2 pr-4 tabular-nums">{pct(s.authenticity_score)}</td>
                  <td className="py-2 pr-4 font-mono text-xs">{s.serial || '—'}</td>
                  <td className="py-2 pr-4 text-slate-400">{s.operator}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Card>
    </div>
  );
}
