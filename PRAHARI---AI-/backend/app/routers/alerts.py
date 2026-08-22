"""Real-time alert WebSocket + alert history."""
from __future__ import annotations

from typing import Set

from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect
from sqlmodel import Session, select, desc

from app.database import get_session
from app.models import Alert

router = APIRouter(tags=["alerts"])

_clients: Set[WebSocket] = set()


async def broadcast(message: dict) -> None:
    dead = []
    for ws in list(_clients):
        try:
            await ws.send_json(message)
        except Exception:
            dead.append(ws)
    for ws in dead:
        _clients.discard(ws)


@router.websocket("/ws/alerts")
async def alerts_ws(ws: WebSocket):
    await ws.accept()
    _clients.add(ws)
    await ws.send_json({"type": "connected", "message": "Prahari command-centre live feed connected"})
    try:
        while True:
            await ws.receive_text()  # keep-alive / ping
    except WebSocketDisconnect:
        _clients.discard(ws)
    except Exception:
        _clients.discard(ws)


@router.get("/api/alerts")
def list_alerts(limit: int = 30, session: Session = Depends(get_session)):
    return session.exec(select(Alert).order_by(desc(Alert.created_at)).limit(limit)).all()


@router.post("/api/alerts/{alert_id}/ack")
def ack(alert_id: int, session: Session = Depends(get_session)):
    a = session.get(Alert, alert_id)
    if a:
        a.acknowledged = True
        session.add(a)
        session.commit()
    return {"ok": bool(a)}
