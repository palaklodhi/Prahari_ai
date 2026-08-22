"""Fraud Network Graph Intelligence endpoints."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from app.database import get_session
from app.models import Account, Transaction
from app.ml.fraud_graph import analyze_network, intelligence_package

router = APIRouter(prefix="/api/fraud", tags=["fraud"])


def _load(session: Session):
    accounts = session.exec(select(Account)).all()
    txns = session.exec(select(Transaction)).all()
    return accounts, txns


@router.get("/network")
def network(session: Session = Depends(get_session)):
    accounts, txns = _load(session)
    return analyze_network(accounts, txns)


@router.get("/rings")
def rings(session: Session = Depends(get_session)):
    accounts, txns = _load(session)
    result = analyze_network(accounts, txns)
    return {"rings": result["rings"], "summary": result["summary"]}


@router.get("/intelligence-package/{ring_id}")
def package(ring_id: int, session: Session = Depends(get_session)):
    accounts, txns = _load(session)
    pkg = intelligence_package(accounts, txns, ring_id)
    if not pkg:
        raise HTTPException(404, "Ring not found")
    return pkg
