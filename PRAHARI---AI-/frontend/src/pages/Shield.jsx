import { useEffect, useRef, useState } from 'react';
import { api } from '../lib/api';
import { pct } from '../lib/format';
import { Card, SectionTitle, Badge } from '../components/ui';

const SUGGESTIONS = [
  'I got a call saying I am under digital arrest by CBI and must transfer money to a safe account.',
  'FedEx says my parcel has drugs and I must pay a customs clearance fee to avoid arrest.',
  'My bank sent a link saying account will be blocked, update KYC with my OTP and password.',
  'A telegram group promises 30% daily returns if I deposit ₹10,000. Is it safe?',
  "Is a message from my son asking to pick him up from the station a scam?",
];

export default function Shield() {
  const [langs, setLangs] = useState([]);
  const [lang, setLang] = useState('en');
  const [channel, setChannel] = useState('whatsapp');
  const [messages, setMessages] = useState([
    { from: 'bot', kind: 'intro', text: 'Namaste 🙏 I am your Citizen Fraud Shield. Forward me any suspicious call, SMS, or payment request and I will tell you instantly if it is a scam — and exactly what to do.' },
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const scrollRef = useRef();

  useEffect(() => { api.shieldLanguages().then(setLangs).catch(() => {}); }, []);
  useEffect(() => { scrollRef.current?.scrollTo({ top: 9e9, behavior: 'smooth' }); }, [messages, loading]);

  async function send(txt) {
    const message = (txt ?? input).trim();
    if (!message) return;
    setMessages((m) => [...m, { from: 'user', text: message }]);
    setInput('');
    setLoading(true);
    try {
      const r = await api.shieldAssess({ message, language: lang, channel });
      setMessages((m) => [...m, { from: 'bot', kind: 'verdict', data: r }]);
    } catch (e) {
      setMessages((m) => [...m, { from: 'bot', text: 'Sorry, I could not analyse that. Please try again.' }]);
    }
    setLoading(false);
  }

  return (
    <div>
      <SectionTitle sub="Conversational AI on WhatsApp, IVR & app that walks citizens through real-time fraud risk assessment — instant verdicts, guided reporting to 1930/NCRB, advisory in 12 Indian languages. Tuned for a very low false-positive rate.">
        🛡️ Citizen Fraud Shield (Multi-channel)
      </SectionTitle>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <Card className="lg:col-span-2 flex flex-col" title="Fraud Shield Assistant"
          subtitle="describe the suspicious call / message"
          right={
            <div className="flex gap-2">
              <select value={channel} onChange={(e) => setChannel(e.target.value)} className="bg-panel2 border border-edge rounded-lg px-2 py-1 text-xs">
                <option value="whatsapp">🟢 WhatsApp</option>
                <option value="ivr">☎️ IVR</option>
                <option value="app">📱 App</option>
              </select>
              <select value={lang} onChange={(e) => setLang(e.target.value)} className="bg-panel2 border border-edge rounded-lg px-2 py-1 text-xs">
                {langs.map((l) => <option key={l.code} value={l.code}>{l.name}</option>)}
              </select>
            </div>
          }>
          <div ref={scrollRef} className="h-[420px] overflow-y-auto space-y-3 pr-1 mb-3">
            {messages.map((m, i) => (
              <div key={i} className={`flex ${m.from === 'user' ? 'justify-end' : 'justify-start'}`}>
                {m.from === 'user' ? (
                  <div className="max-w-[75%] bg-accent text-ink rounded-2xl rounded-br-sm px-4 py-2 text-sm">{m.text}</div>
                ) : m.kind === 'verdict' ? (
                  <VerdictBubble data={m.data} />
                ) : (
                  <div className="max-w-[80%] bg-panel2 border border-edge rounded-2xl rounded-bl-sm px-4 py-2.5 text-sm text-slate-200">{m.text}</div>
                )}
              </div>
            ))}
            {loading && (
              <div className="flex justify-start">
                <div className="bg-panel2 border border-edge rounded-2xl px-4 py-3">
                  <span className="flex gap-1">
                    <span className="w-2 h-2 bg-slate-500 rounded-full animate-bounce" />
                    <span className="w-2 h-2 bg-slate-500 rounded-full animate-bounce [animation-delay:.15s]" />
                    <span className="w-2 h-2 bg-slate-500 rounded-full animate-bounce [animation-delay:.3s]" />
                  </span>
                </div>
              </div>
            )}
          </div>

          <div className="flex gap-2">
            <input value={input} onChange={(e) => setInput(e.target.value)} onKeyDown={(e) => e.key === 'Enter' && send()}
              placeholder="Paste the suspicious message…"
              className="flex-1 bg-panel2 border border-edge rounded-lg px-3 py-2.5 text-sm focus:outline-none focus:border-accent" />
            <button onClick={() => send()} disabled={loading} className="btn btn-primary">Send</button>
          </div>
        </Card>

        <div className="space-y-6">
          <Card title="Try an example" subtitle="tap to test">
            <div className="space-y-2">
              {SUGGESTIONS.map((s, i) => (
                <button key={i} onClick={() => send(s)}
                  className="w-full text-left text-xs p-3 rounded-lg bg-panel2 border border-edge hover:border-accent text-slate-300">
                  {s}
                </button>
              ))}
            </div>
          </Card>

          <Card title="Report Fraud" subtitle="official pathways">
            <div className="space-y-3 text-sm">
              <div className="flex items-center gap-3">
                <span className="text-2xl">☎️</span>
                <div>
                  <p className="text-slate-100 font-semibold">1930</p>
                  <p className="text-xs text-slate-400">National Cyber Crime Helpline</p>
                </div>
              </div>
              <div className="flex items-center gap-3">
                <span className="text-2xl">🌐</span>
                <div>
                  <p className="text-slate-100 font-semibold">cybercrime.gov.in</p>
                  <p className="text-xs text-slate-400">I4C national reporting portal</p>
                </div>
              </div>
              <div className="rounded-lg bg-accent/10 border border-accent/30 p-3 text-xs text-slate-300">
                💡 If money was already transferred, report within the <b>golden hour</b> — banks can freeze the transaction before it is withdrawn.
              </div>
            </div>
          </Card>
        </div>
      </div>
    </div>
  );
}

function VerdictBubble({ data }) {
  const tone = data.risk_band === 'critical' || data.risk_band === 'high'
    ? 'border-danger/40 bg-danger/10'
    : data.risk_band === 'elevated' ? 'border-warn/40 bg-warn/10' : 'border-good/40 bg-good/10';
  return (
    <div className={`max-w-[85%] border rounded-2xl rounded-bl-sm px-4 py-3 ${tone}`}>
      <p className="font-semibold text-slate-100">{data.headline}</p>
      <div className="flex items-center gap-2 mt-1.5">
        <Badge className="bg-panel2 text-slate-200 border-edge">{data.verdict}</Badge>
        <Badge className="bg-panel2 text-slate-300 border-edge">Risk {pct(data.risk_score)}</Badge>
        <Badge className="bg-panel2 text-slate-300 border-edge">{data.scam_type}</Badge>
      </div>
      {data.ai_reply && (
        <div className="mt-2.5 rounded-lg bg-accent/10 border border-accent/25 px-3 py-2">
          <div className="flex items-center gap-1.5 mb-1">
            <span className="text-[10px]">✦</span>
            <span className="text-[10px] uppercase tracking-wide text-accent font-semibold">Gemini assistant</span>
          </div>
          <p className="text-sm text-slate-200 leading-relaxed">{data.ai_reply}</p>
        </div>
      )}
      {data.why && <p className="text-xs text-slate-400 mt-2">{data.why}</p>}

      {data.indicators?.length > 0 && (
        <div className="mt-2 flex flex-wrap gap-1">
          {data.indicators.map((i, idx) => (
            <span key={idx} className="chip bg-panel2 text-slate-400 text-[10px] border border-edge">{i}</span>
          ))}
        </div>
      )}

      <p className="text-xs uppercase tracking-wide text-slate-400 mt-3 mb-1">What you should do</p>
      <ol className="space-y-1">
        {data.guided_steps.map((s, i) => (
          <li key={i} className="text-sm text-slate-200 flex gap-2">
            <span className="text-accent font-semibold">{i + 1}.</span> {s}
          </li>
        ))}
      </ol>

      <div className="mt-3 pt-2 border-t border-edge/60 text-xs text-slate-300">
        📢 {data.advisory_localized}
      </div>
      <div className="mt-1 text-[11px] text-slate-500">Report: {data.report.helpline} · {data.report.portal}</div>
    </div>
  );
}
