import { useEffect, useMemo, useRef, useState, useCallback } from 'react';
import ForceGraph2D from 'react-force-graph-2d';
import { api } from '../lib/api';
import { inr } from '../lib/format';
import { Card, Spinner, SectionTitle, Badge, Stat } from '../components/ui';

const ROLE_COLOR = {
  kingpin: '#f43f5e',
  mule: '#fbbf24',
  layer: '#a78bfa',
  victim: '#38bdf8',
  unknown: '#64748b',
};

export default function Fraud() {
  const [net, setNet] = useState(null);
  const [selectedRing, setSelectedRing] = useState(null);
  const [pkg, setPkg] = useState(null);
  const fgRef = useRef();
  const wrapRef = useRef();
  const [dims, setDims] = useState({ w: 600, h: 460 });

  useEffect(() => { api.fraudNetwork().then(setNet).catch(console.error); }, []);

  useEffect(() => {
    const el = wrapRef.current;
    if (!el) return;
    const ro = new ResizeObserver(() => setDims({ w: el.clientWidth, h: 460 }));
    ro.observe(el);
    return () => ro.disconnect();
  }, [net]);

  const graphData = useMemo(() => {
    if (!net) return { nodes: [], links: [] };
    return {
      nodes: net.graph.nodes.map((n) => ({ ...n })),
      links: net.graph.edges.map((e) => ({ ...e, source: e.source, target: e.target })),
    };
  }, [net]);

  const openPackage = async (ringId) => {
    setSelectedRing(ringId);
    setPkg(null);
    try { setPkg(await api.intelPackage(ringId)); } catch (e) { console.error(e); }
  };

  const downloadPackage = () => {
    if (!pkg) return;
    const blob = new Blob([JSON.stringify(pkg, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url; a.download = `${pkg.package_id}.json`; a.click();
    URL.revokeObjectURL(url);
  };

  const paintNode = useCallback((node, ctx, scale) => {
    const r = 4 + Math.min(8, (node.value || 0) / 120000);
    ctx.beginPath();
    ctx.arc(node.x, node.y, r, 0, 2 * Math.PI);
    ctx.fillStyle = ROLE_COLOR[node.role] || '#64748b';
    ctx.fill();
    if (node.role === 'kingpin') {
      ctx.lineWidth = 2 / scale; ctx.strokeStyle = '#fff'; ctx.stroke();
    }
    if (scale > 1.3) {
      ctx.font = `${10 / scale}px ui-monospace`;
      ctx.fillStyle = '#cbd5e1';
      ctx.textAlign = 'center';
      ctx.fillText(node.holder || node.id, node.x, node.y + r + 9 / scale);
    }
  }, []);

  if (!net) return <Spinner label="Building fraud network graph…" />;
  const s = net.summary;

  return (
    <div>
      <SectionTitle sub="Graph-AI agent that fuses transaction metadata, device fingerprints & phone linkages to map coordinated fraud rings — clustering mules and controllers into court-admissible intelligence packages.">
        🕸️ Fraud Network Graph Intelligence
      </SectionTitle>

      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
        <Stat label="Accounts Mapped" value={s.total_accounts} icon="🏦" />
        <Stat label="Transactions" value={s.total_transactions} icon="🔗" />
        <Stat label="Total Flow Traced" value={inr(s.total_flow)} accent="text-danger" icon="💸" />
        <Stat label="Rings Detected" value={s.rings_detected} accent="text-saffron" icon="⭕" />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-6">
        <Card title="Money-Movement Graph" subtitle="drag nodes · zoom to label · click a node to inspect" className="lg:col-span-2">
          <div ref={wrapRef} className="rounded-lg overflow-hidden bg-ink border border-edge">
            <ForceGraph2D
              ref={fgRef}
              width={dims.w}
              height={dims.h}
              graphData={graphData}
              backgroundColor="#0a0e1a"
              nodeCanvasObject={paintNode}
              nodePointerAreaPaint={(node, color, ctx) => {
                ctx.fillStyle = color;
                ctx.beginPath(); ctx.arc(node.x, node.y, 8, 0, 2 * Math.PI); ctx.fill();
              }}
              linkColor={() => 'rgba(148,163,184,0.25)'}
              linkDirectionalArrowLength={3}
              linkDirectionalArrowRelPos={1}
              linkDirectionalParticles={2}
              linkDirectionalParticleWidth={1.6}
              linkDirectionalParticleColor={() => '#38bdf8'}
              onNodeClick={(n) => n.ring && openPackage(n.ring)}
              cooldownTicks={80}
            />
          </div>
          <div className="flex flex-wrap gap-3 mt-3 text-xs">
            {Object.entries(ROLE_COLOR).map(([role, color]) => (
              <span key={role} className="flex items-center gap-1.5 text-slate-400 capitalize">
                <span className="w-3 h-3 rounded-full" style={{ background: color }} /> {role}
              </span>
            ))}
            <span className="text-slate-500">• animated particles = money flow direction</span>
          </div>
        </Card>

        <Card title="Detected Rings" subtitle="ranked by risk">
          <div className="space-y-3 max-h-[420px] overflow-y-auto pr-1">
            {net.rings.map((r) => (
              <button key={r.ring_id} onClick={() => openPackage(r.ring_id)}
                className={`w-full text-left p-3 rounded-lg border transition-colors ${selectedRing === r.ring_id ? 'border-accent bg-accent/10' : 'border-edge bg-panel2 hover:border-slate-500'}`}>
                <div className="flex items-center justify-between">
                  <span className="font-semibold text-slate-100">Ring #{r.ring_id}</span>
                  <Badge className="bg-danger/15 text-danger border-danger/30">risk {Math.round(r.risk * 100)}%</Badge>
                </div>
                <p className="text-xs text-slate-400 mt-1">{r.size} accounts · {inr(r.total_flow)}</p>
                <div className="flex gap-2 mt-2 text-[11px]">
                  <span className="chip bg-danger/10 text-danger">{r.kingpins.length} kingpin</span>
                  <span className="chip bg-warn/10 text-warn">{r.mules.length} mules</span>
                  <span className="chip bg-panel text-slate-400">{r.shared_devices.length} devices</span>
                </div>
              </button>
            ))}
          </div>
        </Card>
      </div>

      {/* Intelligence package */}
      {selectedRing && (
        <Card
          title={`Intelligence Package · Ring #${selectedRing}`}
          subtitle="auto-generated, court-admissible evidence bundle"
          right={pkg && <button onClick={downloadPackage} className="btn btn-ghost text-xs">⬇ Export JSON</button>}
        >
          {!pkg ? <Spinner /> : (
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-5">
              <div className="lg:col-span-2">
                <div className="flex items-center gap-2 mb-3">
                  <Badge className="bg-danger/15 text-danger border-danger/30">{pkg.classification}</Badge>
                  <span className="font-mono text-xs text-slate-500">{pkg.package_id}</span>
                </div>
                <p className="text-sm text-slate-300 mb-4 leading-relaxed">{pkg.evidence_summary}</p>

                <p className="text-xs uppercase tracking-wide text-slate-400 mb-2">Transaction Ledger</p>
                <div className="overflow-x-auto rounded-lg border border-edge">
                  <table className="w-full text-xs">
                    <thead className="bg-panel2 text-slate-400">
                      <tr>
                        <th className="text-left py-2 px-3">From</th>
                        <th className="text-left py-2 px-3">To</th>
                        <th className="text-right py-2 px-3">Amount</th>
                        <th className="text-left py-2 px-3">Channel</th>
                      </tr>
                    </thead>
                    <tbody>
                      {pkg.transaction_ledger.map((t, i) => (
                        <tr key={i} className="border-t border-edge/50">
                          <td className="py-1.5 px-3 font-mono">{t.src}</td>
                          <td className="py-1.5 px-3 font-mono">{t.dst}</td>
                          <td className="py-1.5 px-3 text-right text-danger">{inr(t.amount)}</td>
                          <td className="py-1.5 px-3 uppercase">{t.channel}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
                <p className="text-[11px] text-slate-500 mt-2">{pkg.admissibility_note}</p>
              </div>

              <div className="space-y-3">
                <div className="bg-panel2 rounded-lg p-3 border border-edge">
                  <p className="text-xs uppercase tracking-wide text-danger mb-2">Controlling Nodes</p>
                  {pkg.ring.kingpins.map((k) => (
                    <div key={k.ref} className="text-sm mb-1">
                      <span className="font-medium text-slate-100">{k.holder}</span>
                      <span className="text-slate-500 text-xs ml-1">({k.ref} · {k.bank})</span>
                    </div>
                  ))}
                </div>
                <div className="bg-panel2 rounded-lg p-3 border border-edge">
                  <p className="text-xs uppercase tracking-wide text-warn mb-2">Mule Accounts</p>
                  {pkg.ring.mules.map((m) => (
                    <div key={m.ref} className="text-sm mb-1">
                      <span className="text-slate-200">{m.holder}</span>
                      <span className="text-slate-500 text-xs ml-1">({m.ref})</span>
                    </div>
                  ))}
                </div>
                <div className="bg-panel2 rounded-lg p-3 border border-edge">
                  <p className="text-xs uppercase tracking-wide text-slate-400 mb-2">Shared Infrastructure</p>
                  <p className="text-xs text-slate-300">Devices: {pkg.ring.shared_devices.join(', ') || '—'}</p>
                  <p className="text-xs text-slate-300 mt-1">Phones: {pkg.ring.shared_phones.join(', ') || '—'}</p>
                  <p className="text-xs text-slate-300 mt-1">Banks: {pkg.ring.banks.join(', ')}</p>
                </div>
              </div>
            </div>
          )}
        </Card>
      )}
    </div>
  );
}
