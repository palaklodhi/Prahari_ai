"""Seed the database with realistic demo data for a compelling command-centre demo."""
from __future__ import annotations

import random
from datetime import datetime, timedelta

from sqlmodel import Session, select

from app.database import engine
from app.models import (
    Account, Transaction, CrimeIncident, ScamSession, CurrencyScan, Alert,
)
from app.ml.scam_detector import detector

random.seed(42)

# (city, state, lat, lon)
CITIES = [
    ("New Delhi", "Delhi", 28.6139, 77.2090),
    ("Mumbai", "Maharashtra", 19.0760, 72.8777),
    ("Bengaluru", "Karnataka", 12.9716, 77.5946),
    ("Hyderabad", "Telangana", 17.3850, 78.4867),
    ("Jamtara", "Jharkhand", 23.9600, 86.8000),
    ("Bharatpur", "Rajasthan", 27.2173, 77.4895),
    ("Nuh", "Haryana", 28.1050, 77.0010),
    ("Kolkata", "West Bengal", 22.5726, 88.3639),
    ("Chennai", "Tamil Nadu", 13.0827, 80.2707),
    ("Pune", "Maharashtra", 18.5204, 73.8567),
    ("Ahmedabad", "Gujarat", 23.0225, 72.5714),
    ("Deoghar", "Jharkhand", 24.4823, 86.6969),
]

CATEGORIES = ["digital_arrest", "counterfeit", "upi_fraud", "phishing"]

SCAM_SCRIPTS_FOR_SESSIONS = [
    ("call", "+91-98XXXXCBI1", "This is Inspector Sharma from CBI Mumbai. A parcel in your name contains illegal drugs. You are under digital arrest. Do not disconnect this video call.", "New Delhi", 28.61, 77.20),
    ("call", "+91-90XXXXED22", "Your Aadhaar is linked to a money laundering case by ED. Transfer funds to the RBI safe custody account to prove innocence and stay on this call.", "Mumbai", 19.07, 72.87),
    ("whatsapp", "+91-70XXXXFEDX", "This is FedEx. Your parcel is held at customs with prohibited items. Pay clearance fee now or face a police case.", "Bengaluru", 12.97, 77.59),
    ("sms", "+91-80XXXXKYC9", "Dear customer your SBI account will be suspended today. Update KYC by clicking this link and entering your net banking password and OTP.", "Hyderabad", 17.38, 78.48),
    ("call", "+91-88XXXXNCB7", "Narcotics Control Bureau here. A FedEx parcel from you had MDMA. Join a Skype interrogation now and do not leave the room. Keep your camera on.", "Pune", 18.52, 73.85),
    ("call", "+91-99XXXXFAM1", "Hi beta it's mummy, reached the station safely, bring the umbrella when you pick me up.", "Kolkata", 22.57, 88.36),
    ("sms", "+91-91XXXXZOM2", "Your Zomato order of two paneer wraps arrives in five minutes, share the OTP with the delivery partner at the door.", "Chennai", 13.08, 80.27),
    ("whatsapp", "+91-73XXXXINV8", "Join our VIP telegram group for guaranteed 30 percent daily returns on crypto. Deposit 10000 and withdraw 50000 tomorrow.", "Ahmedabad", 23.02, 72.57),
]


def seed_all(force: bool = False) -> dict:
    with Session(engine) as s:
        existing = s.exec(select(Account)).first()
        if existing and not force:
            return {"status": "already-seeded"}

        # ---------- Fraud network: two rings + noise ----------
        accounts, transactions = _build_fraud_network()
        for a in accounts:
            s.add(a)
        s.commit()
        for t in transactions:
            s.add(t)
        s.commit()

        # ---------- Crime incidents (geo) ----------
        base = datetime.utcnow()
        for _ in range(260):
            city, state, lat, lon = random.choice(CITIES)
            # cluster tightly around city with jitter; some cities hotter
            jitter = 0.06 if city in ("Jamtara", "Nuh", "Bharatpur", "New Delhi", "Mumbai") else 0.12
            cat = random.choices(CATEGORIES, weights=[4, 2, 5, 3])[0]
            s.add(CrimeIncident(
                created_at=base - timedelta(hours=random.randint(0, 720)),
                category=cat, city=city, state=state,
                lat=lat + random.uniform(-jitter, jitter),
                lon=lon + random.uniform(-jitter, jitter),
                amount_loss=round(random.choice([0, 15000, 45000, 120000, 380000, 1200000, 4200000]) * random.random(), 2),
                severity=random.randint(1, 5),
                description=f"{cat.replace('_',' ').title()} reported in {city}",
            ))
        s.commit()

        # ---------- Scam sessions (run through the real detector) ----------
        for i in range(40):
            channel, cid, text, city, lat, lon = random.choice(SCAM_SCRIPTS_FOR_SESSIONS)
            v = detector.analyze(text)
            s.add(ScamSession(
                created_at=base - timedelta(minutes=random.randint(0, 4000)),
                channel=channel, caller_id=cid,
                transcript=text, duration_sec=random.randint(30, 1800),
                risk_score=v.risk_score, risk_band=v.risk_band,
                scam_type=v.scam_type, indicators=[ind["label"] for ind in v.indicators],
                location=city, lat=lat, lon=lon,
                alerted=v.risk_band in ("high", "critical"),
                status=random.choice(["open", "open", "intercepted", "closed"]),
            ))
        s.commit()

        # ---------- Currency scans ----------
        for i in range(24):
            denom = random.choice([100, 200, 500, 2000])
            verdict = random.choices(["genuine", "suspect", "counterfeit"], weights=[6, 2, 2])[0]
            score = {"genuine": random.uniform(0.75, 0.97), "suspect": random.uniform(0.5, 0.7),
                     "counterfeit": random.uniform(0.15, 0.45)}[verdict]
            city = random.choice(CITIES)[0]
            s.add(CurrencyScan(
                created_at=base - timedelta(hours=random.randint(0, 500)),
                denomination=denom, verdict=verdict, authenticity_score=round(score, 3),
                checks=[], serial=f"{random.randint(0,9)}AB {random.randint(100000,999999)}",
                serial_valid=verdict != "counterfeit",
                operator=random.choice(["Field Officer", "Bank Teller", "PoS Terminal"]),
                location=city,
            ))
        s.commit()

        # ---------- Seed a few live alerts ----------
        for title, body, kind, sev in [
            ("Critical digital-arrest session in progress", "Caller +91-98XXXXCBI1 impersonating CBI — payment imminent", "scam", "critical"),
            ("FICN ₹500 cluster flagged", "3 counterfeit ₹500 notes seized in Bharatpur in 24h", "counterfeit", "high"),
            ("New mule ring surfaced", "Ring-002: 6 accounts, ₹42L flow, shared device", "network", "high"),
        ]:
            s.add(Alert(title=title, body=body, kind=kind, severity=sev))
        s.commit()

        return {"status": "seeded", "accounts": len(accounts), "transactions": len(transactions)}


def _build_fraud_network():
    """Two designed fraud rings (with kingpin + mules + shared infra) plus noise."""
    accounts, txns = [], []
    now = datetime.utcnow()

    # Ring 1 — Jamtara-style, kingpin K1, shared device DEV-A, phone P1
    ring1 = [
        Account(ref="AC1001", holder="Suraj Mandal", bank="SBI", role="kingpin", device_id="DEV-A1", phone="+91-90000A1", account_type="current"),
        Account(ref="AC1002", holder="Ramesh Kumar", bank="PNB", role="mule", device_id="DEV-A1", phone="+91-90000A2"),
        Account(ref="AC1003", holder="Vikas Yadav", bank="HDFC", role="mule", device_id="DEV-A1", phone="+91-90000A2"),
        Account(ref="AC1004", holder="Anil Sah", bank="Axis", role="mule", device_id="DEV-A2", phone="+91-90000A2"),
        Account(ref="AC1005", holder="Deepak Ghosh", bank="ICICI", role="layer", device_id="DEV-A2", phone="+91-90000A3"),
        Account(ref="AC1006", holder="Victim Sharma", bank="SBI", role="victim"),
    ]
    # Ring 2 — call-centre style, kingpin K2, shared device DEV-B
    ring2 = [
        Account(ref="AC2001", holder="Imran Sheikh", bank="Kotak", role="kingpin", device_id="DEV-B1", phone="+91-80000B1", account_type="current"),
        Account(ref="AC2002", holder="Sohail Khan", bank="Yes Bank", role="mule", device_id="DEV-B1", phone="+91-80000B1"),
        Account(ref="AC2003", holder="Faisal Ali", bank="IndusInd", role="mule", device_id="DEV-B1", phone="+91-80000B2"),
        Account(ref="AC2004", holder="Rehan Ansari", bank="Bank of Baroda", role="mule", device_id="DEV-B2", phone="+91-80000B2"),
        Account(ref="AC2005", holder="Victim Nair", bank="Federal", role="victim"),
    ]
    noise = [
        Account(ref="AC3001", holder="Priya Menon", bank="HDFC", role="unknown", device_id="DEV-X", phone="+91-70000X1"),
        Account(ref="AC3002", holder="Karan Shah", bank="SBI", role="unknown", device_id="DEV-Y", phone="+91-70000X2"),
    ]
    accounts = ring1 + ring2 + noise

    def add_tx(src, dst, amt, ch, hrs):
        txns.append(Transaction(src_ref=src, dst_ref=dst, amount=amt, channel=ch,
                                created_at=now - timedelta(hours=hrs), flagged=True))

    # Ring 1 flows: victim -> mules -> kingpin (layering)
    add_tx("AC1006", "AC1002", 480000, "imps", 40)
    add_tx("AC1002", "AC1003", 230000, "upi", 39)
    add_tx("AC1002", "AC1004", 220000, "upi", 39)
    add_tx("AC1003", "AC1001", 210000, "imps", 38)
    add_tx("AC1004", "AC1005", 190000, "imps", 38)
    add_tx("AC1005", "AC1001", 175000, "neft", 37)
    add_tx("AC1001", "AC1001", 0, "cash", 36)  # self-ref noise avoided in graph

    # Ring 2 flows
    add_tx("AC2005", "AC2002", 620000, "imps", 20)
    add_tx("AC2002", "AC2003", 300000, "upi", 19)
    add_tx("AC2002", "AC2004", 300000, "upi", 19)
    add_tx("AC2003", "AC2001", 290000, "imps", 18)
    add_tx("AC2004", "AC2001", 285000, "neft", 18)

    # noise
    add_tx("AC3001", "AC3002", 12000, "upi", 10)
    return accounts, txns
