"""Command-centre dashboard aggregation."""
from __future__ import annotations

from datetime import datetime, timedelta

from fastapi import APIRouter, Depends
from sqlmodel import Session, select, desc

from app.database import get_session
from app.models import ScamSession, CurrencyScan, Account, Transaction, CrimeIncident, Alert
from app.ml.fraud_graph import analyze_network
from app.ml.geo_intel import compute_hotspots

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])


@router.get("/overview")
def overview(session: Session = Depends(get_session)):
    scams = session.exec(select(ScamSession)).all()
    scans = session.exec(select(CurrencyScan)).all()
    incidents = session.exec(select(CrimeIncident)).all()
    accounts = session.exec(select(Account)).all()
    txns = session.exec(select(Transaction)).all()

    net = analyze_network(accounts, txns)
    geo = compute_hotspots(incidents)

    high_risk_scams = sum(1 for s in scams if s.risk_band in ("high", "critical"))
    counterfeit = sum(1 for c in scans if c.verdict == "counterfeit")
    total_loss = sum(i.amount_loss for i in incidents)
    prevented = sum(1 for s in scams if s.status == "intercepted")

    # 14-day trend of scam sessions
    now = datetime.utcnow()
    trend = []
    for d in range(13, -1, -1):
        day = (now - timedelta(days=d)).date()
        cnt = sum(1 for s in scams if s.created_at.date() == day)
        hi = sum(1 for s in scams if s.created_at.date() == day and s.risk_band in ("high", "critical"))
        trend.append({"date": day.isoformat(), "sessions": cnt, "high_risk": hi})

    return {
        "kpis": {
            "scam_sessions": len(scams),
            "high_risk_scams": high_risk_scams,
            "sessions_intercepted": prevented,
            "counterfeit_detected": counterfeit,
            "currency_scans": len(scans),
            "fraud_rings": net["summary"].get("rings_detected", 0),
            "accounts_in_rings": net["summary"].get("accounts_in_rings", 0),
            "network_flow": net["summary"].get("total_flow", 0),
            "crime_incidents": len(incidents),
            "critical_hotspots": geo["summary"].get("critical_hotspots", 0),
            "total_loss": round(total_loss, 2),
        },
        "scam_trend": trend,
        "top_hotspots": geo["hotspots"][:5],
        "top_rings": net["rings"][:3],
        "scam_by_type": _count(scams, "scam_type"),
        "incidents_by_category": _count(incidents, "category"),
    }


@router.get("/feed")
def feed(limit: int = 20, session: Session = Depends(get_session)):
    alerts = session.exec(select(Alert).order_by(desc(Alert.created_at)).limit(limit)).all()
    return alerts


def _count(rows, attr):
    out = {}
    for r in rows:
        k = getattr(r, attr)
        out[k] = out.get(k, 0) + 1
    return out
