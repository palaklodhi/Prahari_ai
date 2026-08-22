export function inr(n) {
  if (n == null) return '—';
  if (n >= 1e7) return `₹${(n / 1e7).toFixed(2)} Cr`;
  if (n >= 1e5) return `₹${(n / 1e5).toFixed(2)} L`;
  if (n >= 1e3) return `₹${(n / 1e3).toFixed(1)}K`;
  return `₹${Math.round(n)}`;
}

export function num(n) {
  return (n ?? 0).toLocaleString('en-IN');
}

export function pct(n) {
  return `${Math.round((n ?? 0) * 100)}%`;
}

export const bandColor = {
  critical: 'text-danger',
  high: 'text-warn',
  elevated: 'text-amber-300',
  low: 'text-good',
};

export const bandBg = {
  critical: 'bg-danger/15 text-danger border-danger/30',
  high: 'bg-warn/15 text-warn border-warn/30',
  elevated: 'bg-amber-300/10 text-amber-300 border-amber-300/30',
  low: 'bg-good/10 text-good border-good/30',
};

export const verdictBg = {
  counterfeit: 'bg-danger/15 text-danger border-danger/30',
  suspect: 'bg-warn/15 text-warn border-warn/30',
  genuine: 'bg-good/10 text-good border-good/30',
};

export function timeAgo(iso) {
  const d = new Date(iso);
  const s = Math.floor((Date.now() - d.getTime()) / 1000);
  if (s < 60) return `${s}s ago`;
  if (s < 3600) return `${Math.floor(s / 60)}m ago`;
  if (s < 86400) return `${Math.floor(s / 3600)}h ago`;
  return `${Math.floor(s / 86400)}d ago`;
}
