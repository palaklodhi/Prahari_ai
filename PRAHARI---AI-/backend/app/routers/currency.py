"""Counterfeit Currency Identification endpoints."""
from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends, File, Form, UploadFile
from sqlmodel import Session, select, desc

from app.database import get_session
from app.models import CurrencyScan, Alert
from app.ml.currency_analyzer import analyzer, DENOM_PROFILES

router = APIRouter(prefix="/api/currency", tags=["currency"])


@router.get("/denominations")
def denominations():
    return [{"denomination": d, "base_color": p["name"]} for d, p in DENOM_PROFILES.items()]


@router.post("/scan")
def scan(
    denomination: int = Form(...),
    serial: Optional[str] = Form(None),
    operator: Optional[str] = Form("Field Officer"),
    location: Optional[str] = Form(None),
    file: UploadFile = File(...),
    session: Session = Depends(get_session),
):
    image_bytes = file.file.read()
    result = analyzer.analyze(image_bytes, denomination, serial)

    rec = CurrencyScan(
        denomination=result.denomination, verdict=result.verdict,
        authenticity_score=result.authenticity_score, checks=result.checks,
        serial=result.serial, serial_valid=result.serial_valid,
        operator=operator, location=location,
    )
    session.add(rec)
    session.commit()
    session.refresh(rec)

    if result.verdict == "counterfeit":
        session.add(Alert(
            kind="counterfeit", severity="high",
            title=f"Counterfeit ₹{denomination} detected",
            body=f"Authenticity {result.authenticity_score:.0%} — {result.recommendation}",
            ref_id=rec.id,
        ))
        session.commit()

    return {
        "scan_id": rec.id,
        "denomination": result.denomination,
        "verdict": result.verdict,
        "authenticity_score": result.authenticity_score,
        "checks": result.checks,
        "serial": result.serial,
        "serial_valid": result.serial_valid,
        "dominant_color": result.dominant_color,
        "recommendation": result.recommendation,
    }


@router.get("/scans")
def list_scans(limit: int = 50, session: Session = Depends(get_session)):
    return session.exec(select(CurrencyScan).order_by(desc(CurrencyScan.created_at)).limit(limit)).all()


@router.get("/stats")
def stats(session: Session = Depends(get_session)):
    rows = session.exec(select(CurrencyScan)).all()
    by_verdict = {}
    by_denom = {}
    for r in rows:
        by_verdict[r.verdict] = by_verdict.get(r.verdict, 0) + 1
        by_denom[str(r.denomination)] = by_denom.get(str(r.denomination), 0) + 1
    total = len(rows)
    genuine = by_verdict.get("genuine", 0)
    return {
        "total_scans": total,
        "counterfeit": by_verdict.get("counterfeit", 0),
        "suspect": by_verdict.get("suspect", 0),
        "detection_rate": round((by_verdict.get("counterfeit", 0) + by_verdict.get("suspect", 0)) / total, 3) if total else 0,
        "by_verdict": by_verdict,
        "by_denomination": by_denom,
    }
