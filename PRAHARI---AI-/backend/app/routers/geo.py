"""Geospatial Crime Pattern Intelligence endpoints."""
from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends
from sqlmodel import Session, select

from app.database import get_session
from app.models import CrimeIncident
from app.ml.geo_intel import compute_hotspots

router = APIRouter(prefix="/api/geo", tags=["geo"])


@router.get("/incidents")
def incidents(category: Optional[str] = None, limit: int = 500, session: Session = Depends(get_session)):
    q = select(CrimeIncident)
    if category:
        q = q.where(CrimeIncident.category == category)
    rows = session.exec(q.limit(limit)).all()
    return rows


@router.get("/hotspots")
def hotspots(session: Session = Depends(get_session)):
    rows = session.exec(select(CrimeIncident)).all()
    return compute_hotspots(rows)
