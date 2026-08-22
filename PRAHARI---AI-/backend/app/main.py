"""Prahari — Digital Public Safety Intelligence Platform (FastAPI backend)."""
from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import APP_NAME, APP_VERSION, CORS_ORIGINS
from app.database import init_db
from app.ml.scam_detector import detector
from app.routers import scam, currency, fraud, geo, shield, dashboard, alerts, ai


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    detector.load_or_train()
    from app.seed import seed_all
    seed_all()
    yield


app = FastAPI(title=APP_NAME, version=APP_VERSION, lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(dashboard.router)
app.include_router(scam.router)
app.include_router(currency.router)
app.include_router(fraud.router)
app.include_router(geo.router)
app.include_router(shield.router)
app.include_router(alerts.router)
app.include_router(ai.router)


@app.get("/api/health")
def health():
    return {"status": "ok", "app": APP_NAME, "version": APP_VERSION}


@app.get("/")
def root():
    return {
        "app": APP_NAME,
        "version": APP_VERSION,
        "modules": [
            "Digital Arrest Scam Detection",
            "Counterfeit Currency Identification",
            "Fraud Network Graph Intelligence",
            "Geospatial Crime Pattern Intelligence",
            "Citizen Fraud Shield (multi-channel)",
        ],
        "docs": "/docs",
    }
