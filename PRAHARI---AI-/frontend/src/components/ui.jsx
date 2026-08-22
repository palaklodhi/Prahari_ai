export function Card({ title, subtitle, right, children, className = '' }) {
  return (
    <div className={`card ${className}`}>
      {(title || right) && (
        <div className="card-h">
          <div>
            {title && <h3 className="font-semibold text-slate-100">{title}</h3>}
            {subtitle && <p className="text-xs text-slate-400 mt-0.5">{subtitle}</p>}
          </div>
          {right}
        </div>
      )}
      <div className="p-5">{children}</div>
    </div>
  );
}

export function Stat({ label, value, sub, accent = 'text-slate-100', icon }) {
  return (
    <div className="card p-4 grid-glow">
      <div className="flex items-start justify-between">
        <div>
          <p className="text-xs uppercase tracking-wide text-slate-400">{label}</p>
          <p className={`stat-num mt-1 ${accent}`}>{value}</p>
          {sub && <p className="text-xs text-slate-500 mt-1">{sub}</p>}
        </div>
        {icon && <span className="text-2xl opacity-70">{icon}</span>}
      </div>
    </div>
  );
}

export function Badge({ children, className = '' }) {
  return <span className={`chip border ${className}`}>{children}</span>;
}

export function Spinner({ label = 'Loading…' }) {
  return (
    <div className="flex items-center gap-3 text-slate-400 text-sm py-8 justify-center">
      <span className="w-4 h-4 border-2 border-accent border-t-transparent rounded-full animate-spin" />
      {label}
    </div>
  );
}

export function Progress({ value, tone = 'bg-accent' }) {
  return (
    <div className="w-full h-2 bg-edge rounded-full overflow-hidden">
      <div className={`h-full ${tone} transition-all`} style={{ width: `${Math.round((value || 0) * 100)}%` }} />
    </div>
  );
}

export function SectionTitle({ children, sub }) {
  return (
    <div className="mb-5">
      <h1 className="text-2xl font-bold text-slate-100">{children}</h1>
      {sub && <p className="text-slate-400 text-sm mt-1">{sub}</p>}
    </div>
  );
}
