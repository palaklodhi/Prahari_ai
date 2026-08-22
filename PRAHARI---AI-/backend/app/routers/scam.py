"""Digital Arrest Scam Detection & Alerting endpoints."""
from __future__ import annotations

from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlmodel import Session, select, desc

from app.database import get_session
from app.models import ScamSession, Alert
from app.ml.scam_detector import detector
from app.routers.alerts import broadcast
from app.services import gemini

router = APIRouter(prefix="/api/scam", tags=["scam"])


class AnalyzeRequest(BaseModel):
    transcript: str
    channel: str = "call"
    caller_id: str = "unknown"
    duration_sec: int = 0
    location: Optional[str] = None
    lat: Optional[float] = None
    lon: Optional[float] = None
    persist: bool = True
    deep_analysis: bool = False  # request an extra Gemini reasoning pass


_SCAM_SYSTEM = (
    "You are Prahari Analyst, a fraud-intelligence copilot for Indian law "
    "enforcement. Given a call/message transcript and a classifier verdict, "
    "explain in 2-3 sentences WHY this is (or isn't) a scam, what the fraudster "
    "is trying to achieve, and the single most important intervention. Never "
    "override the classifier's risk band."
)


def _ai_analysis(transcript: str, v) -> Optional[str]:
    if not gemini.is_enabled():
        return None
    indicators = ", ".join(i["label"] for i in v.indicators) or "none"
    prompt = (
        f"Transcript: \"{transcript}\"\n\n"
        f"Classifier verdict: risk band {v.risk_band} ({v.risk_score:.0%}), "
        f"likely type {v.scam_type_label}. Indicators: {indicators}."
    )
    return gemini.generate(prompt, system=_SCAM_SYSTEM, temperature=0.3, max_tokens=350)


@router.post("/analyze")
async def analyze(req: AnalyzeRequest, session: Session = Depends(get_session)):
    v = detector.analyze(req.transcript)
    result = {
        "risk_score": v.risk_score,
        "risk_band": v.risk_band,
        "scam_type": v.scam_type,
        "scam_type_label": v.scam_type_label,
        "model_probability": v.model_probability,
        "rule_score": v.rule_score,
        "indicators": v.indicators,
        "recommended_action": v.recommended_action,
        "explanation": v.explanation,
    }

    if req.deep_analysis:
        result["ai_analysis"] = _ai_analysis(req.transcript, v)
        result["ai_powered"] = result["ai_analysis"] is not None

    if req.persist:
        rec = ScamSession(
            channel=req.channel, caller_id=req.caller_id, transcript=req.transcript,
            duration_sec=req.duration_sec, risk_score=v.risk_score, risk_band=v.risk_band,
            scam_type=v.scam_type, indicators=[i["label"] for i in v.indicators],
            location=req.location, lat=req.lat, lon=req.lon,
            alerted=v.risk_band in ("high", "critical"),
        )
        session.add(rec)
        session.commit()
        session.refresh(rec)
        result["session_id"] = rec.id

        if v.risk_band in ("high", "critical"):
            alert = Alert(
                kind="scam", severity=v.risk_band,
                title=f"{v.scam_type_label} scam detected ({v.risk_band.upper()})",
                body=f"Caller {req.caller_id} — {v.explanation}",
                ref_id=rec.id,
            )
            session.add(alert)
            session.commit()
            await broadcast({
                "type": "alert", "kind": "scam", "severity": v.risk_band,
                "title": alert.title, "body": alert.body,
                "caller_id": req.caller_id, "risk_score": v.risk_score,
                "ts": datetime.utcnow().isoformat(),
            })

    return result


@router.get("/sessions")
def list_sessions(limit: int = 50, session: Session = Depends(get_session)):
    rows = session.exec(select(ScamSession).order_by(desc(ScamSession.created_at)).limit(limit)).all()
    return rows


@router.get("/stats")
def stats(session: Session = Depends(get_session)):
    rows = session.exec(select(ScamSession)).all()
    total = len(rows)
    by_band = {}
    by_type = {}
    for r in rows:
        by_band[r.risk_band] = by_band.get(r.risk_band, 0) + 1
        by_type[r.scam_type] = by_type.get(r.scam_type, 0) + 1
    intercepted = sum(1 for r in rows if r.status == "intercepted")
    return {
        "total_sessions": total,
        "high_risk": by_band.get("high", 0) + by_band.get("critical", 0),
        "intercepted": intercepted,
        "by_band": by_band,
        "by_type": by_type,
    }


# Sample transcripts for the live demo console
@router.get("/samples")
def samples():
    return [
        {"label": "Digital Arrest (CBI)", "channel": "call",
         "text": "This is Inspector Sharma from CBI Mumbai. A parcel in your name contains illegal drugs and passports. You are under digital arrest. Do not disconnect this video call. Transfer your savings to the RBI safe custody account for verification."},
        {"label": "ED money-laundering", "channel": "call",
         "text": "Sir your Aadhaar is linked to a money laundering case by the Enforcement Directorate. Stay on this call, keep your camera on, and deposit the security amount to prove your innocence."},
        {"label": "FedEx courier scam", "channel": "whatsapp",
         "text": "This is FedEx customer care. Your parcel is held at customs and contains prohibited items. Pay a customs clearance fee now or face legal action and arrest."},
        {"label": "KYC / OTP phishing", "channel": "sms",
         "text": "Dear customer your account will be suspended today. Update your KYC by clicking this link and entering your net banking password and OTP immediately."},
        {"label": "Genuine delivery call", "channel": "call",
         "text": "Hi this is Rahul from Zomato, your order of two paneer wraps is arriving in five minutes, please share the OTP with the delivery partner at the door."},
        {"label": "Genuine family message", "channel": "sms",
         "text": "Hi beta, it's mummy. Reached the station safely. Bring the umbrella when you come to pick me up, it looks like rain."},
    ]
