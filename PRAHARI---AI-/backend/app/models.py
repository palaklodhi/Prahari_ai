"""SQLModel database tables for the Prahari platform."""
from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlmodel import Field, SQLModel, Column, JSON


def _now() -> datetime:
    return datetime.utcnow()


class ScamSession(SQLModel, table=True):
    """A telecom / message session evaluated by the Digital Arrest scam classifier."""
    __tablename__ = "scam_sessions"

    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=_now, index=True)
    channel: str = Field(default="call")  # call | sms | whatsapp
    caller_id: str = Field(index=True)
    victim_hint: Optional[str] = None
    transcript: str
    duration_sec: int = 0
    risk_score: float = Field(default=0.0, index=True)
    risk_band: str = Field(default="low", index=True)  # low | elevated | high | critical
    scam_type: str = Field(default="unknown")
    indicators: list = Field(default_factory=list, sa_column=Column(JSON))
    location: Optional[str] = None
    lat: Optional[float] = None
    lon: Optional[float] = None
    alerted: bool = False
    status: str = Field(default="open")  # open | intercepted | closed


class CurrencyScan(SQLModel, table=True):
    """A counterfeit-currency scan result from the CV agent."""
    __tablename__ = "currency_scans"

    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=_now, index=True)
    denomination: int = 0
    verdict: str = Field(default="unknown")  # genuine | suspect | counterfeit
    authenticity_score: float = 0.0
    checks: list = Field(default_factory=list, sa_column=Column(JSON))
    serial: Optional[str] = None
    serial_valid: Optional[bool] = None
    operator: Optional[str] = None
    location: Optional[str] = None


class Account(SQLModel, table=True):
    """Financial account / entity node in the fraud graph."""
    __tablename__ = "accounts"

    id: Optional[int] = Field(default=None, primary_key=True)
    ref: str = Field(index=True, unique=True)
    holder: str
    bank: str
    account_type: str = "savings"  # savings | current | wallet
    role: str = "unknown"  # mule | kingpin | victim | layer | unknown
    device_id: Optional[str] = None
    phone: Optional[str] = None
    risk: float = 0.0
    flagged: bool = False


class Transaction(SQLModel, table=True):
    """Edge in the fraud graph — money movement between accounts."""
    __tablename__ = "transactions"

    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=_now, index=True)
    src_ref: str = Field(index=True)
    dst_ref: str = Field(index=True)
    amount: float = 0.0
    channel: str = "imps"  # imps | upi | neft | cash
    flagged: bool = False


class CrimeIncident(SQLModel, table=True):
    """Geolocated crime/fraud/seizure incident for geospatial intelligence."""
    __tablename__ = "crime_incidents"

    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=_now, index=True)
    category: str = "digital_arrest"  # digital_arrest | counterfeit | upi_fraud | phishing
    city: str = ""
    state: str = ""
    district: Optional[str] = None
    lat: float = 0.0
    lon: float = 0.0
    amount_loss: float = 0.0
    severity: int = 1  # 1..5
    description: Optional[str] = None


class Alert(SQLModel, table=True):
    """Operational alert surfaced in the command center."""
    __tablename__ = "alerts"

    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=_now, index=True)
    kind: str = "scam"  # scam | counterfeit | network | geo
    severity: str = "high"  # info | warning | high | critical
    title: str = ""
    body: str = ""
    ref_id: Optional[int] = None
    acknowledged: bool = False
