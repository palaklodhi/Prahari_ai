import { useEffect, useState } from 'react';
import { MapContainer, TileLayer, CircleMarker, Popup, LayerGroup } from 'react-leaflet';
import { api } from '../lib/api';
import { inr, num } from '../lib/format';
import { Card, Spinner, SectionTitle, Badge, Stat } from '../components/ui';

const CAT_COLOR = {
  digital_arrest: '#f43f5e',
  counterfeit: '#fbbf24',
  upi_fraud: '#38bdf8',
  phishing: '#a78bfa',
};

const PRIORITY_COLOR = { critical: '#f43f5e', high: '#fb923c', watch: '#38bdf8' };

export default function Geo() {
  const [data, setData] = useState(null);
  const [incidents, setIncidents] = useState([]);
  const [cat, setCat] = useState('');
  const [layer, setLayer] = useState('hotspots');

  useEffect(() => { api.hotspots().then(setData).catch(console.error); }, []);
  useEffect(() => { api.incidents(cat).then(setIncidents).catch(() => {}); }, [cat]);

  if (!data) return <Spinner label="Computing crime hotspots…" />;
  const s = data.summary;

  return (
    <div>
      <SectionTitle sub="Geospatial AI layer that maps fraud complaints, counterfeit seizures & cybercrime hotspots — enabling patrol prioritisation, resource deployment & inter-district intelligence sharing in near real-time.">
        🗺️ Geospatial Crime Pattern Intelligence
      </SectionTitle>

      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
        <Stat label="Incidents Mapped" value={num(s.total_incidents)} icon="📍" />
        <Stat label="Active Hotspots" value={s.hotspots} accent="text-warn" icon="🔥" />
        <Stat label="Critical Clusters" value={s.critical_hotspots} accent="text-danger" icon="🚨" />
        <Stat label="Mapped Losses" value={inr(s.total_loss)} accent="text-danger" icon="💰" />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-6">
        <Card
          title="Live Crime Map — India"
          subtitle={layer === 'hotspots' ? 'clustered hotspots sized by intensity' : 'individual incidents by category'}
          className="lg:col-span-2"
          right={
            <div className="flex gap-2">
              <button onClick={() => setLayer('hotspots')} className={`chip border ${layer === 'hotspots' ? 'bg-accent/15 text-accent border-accent/40' : 'bg-panel2 border-edge text-slate-400'}`}>Hotspots</button>
              <button onClick={() => setLayer('incidents')} className={`chip border ${layer === 'incidents' ? 'bg-accent/15 text-accent border-accent/40' : 'bg-panel2 border-edge text-slate-400'}`}>Incidents</button>
            </div>
          }
        >
          <div className="rounded-lg overflow-hidden border border-edge" style={{ height: 460 }}>
            <MapContainer center={[22.9, 79.5]} zoom={5} style={{ height: '100%', width: '100%' }} scrollWheelZoom>
              <TileLayer
                attribution='&copy; OpenStreetMap'
                url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"
              />
              {layer === 'hotspots' ? (
                <LayerGroup>
                  {data.hotspots.map((h) => (
                    <CircleMarker key={h.id} center={[h.lat, h.lon]}
                      radius={6 + h.intensity * 22}
                      pathOptions={{ color: PRIORITY_COLOR[h.priority], fillColor: PRIORITY_COLOR[h.priority], fillOpacity: 0.35, weight: 1 }}>
                      <Popup>
                        <div className="text-sm">
                          <b>{h.city}, {h.state}</b><br />
                          Priority: <b style={{ color: PRIORITY_COLOR[h.priority] }}>{h.priority}</b><br />
                          {h.incident_count} incidents · {inr(h.total_loss)}<br />
                          Dominant: {h.dominant_category.replace(/_/g, ' ')}<br />
                          <span className="text-xs opacity-80">{h.recommendation}</span>
                        </div>
                      </Popup>
                    </CircleMarker>
                  ))}
                </LayerGroup>
              ) : (
                <LayerGroup>
                  {incidents.map((i) => (
                    <CircleMarker key={i.id} center={[i.lat, i.lon]} radius={3 + i.severity}
                      pathOptions={{ color: CAT_COLOR[i.category], fillColor: CAT_COLOR[i.category], fillOpacity: 0.6, weight: 0.5 }}>
                      <Popup>
                        <div className="text-sm">
                          <b>{i.city}, {i.state}</b><br />
                          {i.category.replace(/_/g, ' ')} · severity {i.severity}<br />
                          Loss: {inr(i.amount_loss)}
                        </div>
                      </Popup>
                    </CircleMarker>
                  ))}
                </LayerGroup>
              )}
            </MapContainer>
          </div>
          <div className="flex flex-wrap gap-3 mt-3 text-xs">
            {layer === 'incidents' ? Object.entries(CAT_COLOR).map(([k, c]) => (
              <button key={k} onClick={() => setCat(cat === k ? '' : k)}
                className={`flex items-center gap-1.5 capitalize ${cat === k ? 'text-slate-100' : 'text-slate-400'}`}>
                <span className="w-3 h-3 rounded-full" style={{ background: c }} /> {k.replace(/_/g, ' ')}
              </button>
            )) : Object.entries(PRIORITY_COLOR).map(([k, c]) => (
              <span key={k} className="flex items-center gap-1.5 capitalize text-slate-400">
                <span className="w-3 h-3 rounded-full" style={{ background: c }} /> {k}
              </span>
            ))}
          </div>
        </Card>

        <div className="space-y-6">
          <Card title="Priority Deployment Queue" subtitle="top hotspots">
            <div className="space-y-3 max-h-52 overflow-y-auto pr-1">
              {data.hotspots.slice(0, 6).map((h) => (
                <div key={h.id} className="p-3 rounded-lg bg-panel2 border border-edge">
                  <div className="flex items-center justify-between">
                    <span className="text-sm font-medium text-slate-100">{h.city}</span>
                    <Badge className={h.priority === 'critical' ? 'bg-danger/15 text-danger border-danger/30' : h.priority === 'high' ? 'bg-warn/15 text-warn border-warn/30' : 'bg-accent/15 text-accent border-accent/30'}>
                      {h.priority}
                    </Badge>
                  </div>
                  <p className="text-[11px] text-slate-400 mt-1">{h.recommendation}</p>
                </div>
              ))}
            </div>
          </Card>

          <Card title="State Intelligence Rollup" subtitle="inter-district sharing">
            <div className="space-y-2 max-h-52 overflow-y-auto pr-1">
              {data.state_rollup.slice(0, 8).map((r) => (
                <div key={r.state} className="flex items-center justify-between text-sm">
                  <span className="text-slate-200">{r.state}</span>
                  <span className="text-slate-400 text-xs">{r.incidents} inc · <span className="text-danger">{inr(r.loss)}</span></span>
                </div>
              ))}
            </div>
          </Card>
        </div>
      </div>
    </div>
  );
}
