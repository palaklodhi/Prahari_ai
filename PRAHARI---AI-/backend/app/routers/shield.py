"""Citizen Fraud Shield (multi-channel) endpoints."""
from __future__ import annotations

from fastapi import APIRouter
from pydantic import BaseModel

from app.ml.citizen_shield import assess, SUPPORTED_LANGUAGES

router = APIRouter(prefix="/api/shield", tags=["shield"])


class ShieldRequest(BaseModel):
    message: str
    language: str = "en"
    channel: str = "whatsapp"


@router.post("/assess")
def shield_assess(req: ShieldRequest):
    return assess(req.message, req.language, req.channel)


@router.get("/languages")
def languages():
    return SUPPORTED_LANGUAGES
