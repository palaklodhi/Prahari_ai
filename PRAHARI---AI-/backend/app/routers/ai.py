"""AI augmentation status + Gemini-powered analyst assistant."""
from __future__ import annotations

from fastapi import APIRouter
from pydantic import BaseModel

from app.services import gemini

router = APIRouter(prefix="/api/ai", tags=["ai"])


@router.get("/status")
def ai_status():
    """Tells the UI whether the Gemini augmentation layer is connected."""
    return gemini.status()


class AskRequest(BaseModel):
    question: str
    context: str = ""


ANALYST_SYSTEM = (
    "You are Prahari Analyst, an AI copilot inside a law-enforcement fraud "
    "intelligence command centre in India. You help officers reason about "
    "digital-arrest scams, counterfeit currency (FICN), mule networks and "
    "cybercrime hotspots. Be concise, factual, and operationally useful. Cite "
    "the National Cyber Crime Helpline 1930 / cybercrime.gov.in where relevant."
)


@router.post("/ask")
def ai_ask(req: AskRequest):
    """Free-form analyst assistant. Requires a configured Gemini key."""
    if not gemini.is_enabled():
        return {
            "enabled": False,
            "answer": "Gemini is not configured. Set GEMINI_API_KEY (from Google AI "
                      "Studio) in backend/.env to enable the AI analyst assistant.",
        }
    prompt = req.question if not req.context else f"Context:\n{req.context}\n\nQuestion: {req.question}"
    answer = gemini.generate(prompt, system=ANALYST_SYSTEM, temperature=0.4, max_tokens=700)
    return {
        "enabled": True,
        "answer": answer or "The AI analyst could not produce a response right now. Please try again.",
    }
