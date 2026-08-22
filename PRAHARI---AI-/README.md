<div align="center">

# 🛡️ Prahari
### AI for Digital Public Safety — Defeating Counterfeiting, Fraud & Digital Arrest Scams

**A unified, AI-powered Digital Public Safety Intelligence platform that equips law
enforcement, financial institutions, and citizens to detect, disrupt, and respond to
digital fraud networks, counterfeit currency, and organised scam operations — shifting
from reactive investigation to predictive threat neutralisation.**

*Theme: Smart Cities · Public Safety · Digital Trust · Geospatial Law Enforcement*

</div>

---

## The Problem

India registered **1.14 million cybercrime complaints in 2023** (up 60% YoY). "Digital
arrest" scams — where fraudsters impersonate CBI/ED/Customs officers over video calls —
defrauded citizens of **₹1,776 crore in just the first nine months of 2024**. The RBI's
2025 report flagged **record FICN (Fake Indian Currency Note) seizures**, with
high-denomination ₹500 fakes good enough to defeat manual detection.

What law enforcement lacks is not evidence *after* the fact — it is **intelligence
before mass victimisation**, and reliable tools to detect threats at the point of
contact. Prahari delivers exactly that convergence.

## The Five Pillars

| # | Module | What it does |
|---|--------|--------------|
| 1 | 📞 **Digital Arrest Scam Detection & Alerting** | Real-time NLP classifier flags active scam sessions (call/SMS/WhatsApp) *before* financial transfer, with explainable indicators + automated telecom/victim alerting. |
| 2 | 💵 **Counterfeit Currency Identification Agent** | On-device computer vision verifies notes across all denominations — micro-print, security-thread, colour, serial validation — with a per-feature authenticity report. |
| 3 | 🕸️ **Fraud Network Graph Intelligence** | Graph-AI maps coordinated mule rings from transaction + device + phone linkages, and exports court-admissible intelligence packages. |
| 4 | 🗺️ **Geospatial Crime Pattern Intelligence** | Clusters incidents into hotspots for patrol prioritisation, resource deployment, and inter-district intelligence sharing. |
| 5 | 🛡️ **Citizen Fraud Shield (multi-channel)** | Conversational AI (WhatsApp/IVR/app) gives citizens instant fraud verdicts, guided reporting to 1930/NCRB, and advisory in **12 Indian languages**. |

All five feed a **live multi-agency Command Center** with real-time WebSocket alerting.

---

## Quick Start

### Option A — one command (local)
```bash
./start.sh
```
Then open **http://localhost:5173** (API docs at http://localhost:8000/docs).

### Option B — Docker
```bash
docker compose up --build
```
Frontend on **http://localhost:8080**, backend on **http://localhost:8000**.

### Option C — run each side manually
```bash
# Backend
cd backend && python3 -m venv .venv && ./.venv/bin/pip install -r requirements.txt
./.venv/bin/uvicorn app.main:app --reload --port 8000

# Frontend (new terminal)
cd frontend && npm install && npm run dev
```

The database auto-creates, the ML models auto-train, and realistic demo data
(fraud rings, scam sessions, hotspots, counterfeit scans) auto-seeds on first boot.

---

## 🔮 Optional: Add Google Gemini (Google AI Studio)

Prahari works fully offline on its built-in ML/rule engines. Plug in a **Gemini**
key to unlock an AI augmentation layer — natural-language analyst reasoning on
scam verdicts, and warm, multilingual conversational replies in the Citizen Shield.

> The deterministic ML/rules always decide the **risk verdict** (that's what keeps
> the system auditable). Gemini only adds explanation and conversation on top —
> it can never override a risk band.

**Setup (30 seconds):**
1. Get a free key at **https://aistudio.google.com/app/apikey**
2. `cp backend/.env.example backend/.env`
3. Paste your key: `GEMINI_API_KEY=AIza...`
4. Restart the backend (`./start.sh`). The sidebar now shows **“Gemini AI online”**.

For Docker: `GEMINI_API_KEY=AIza... docker compose up --build`

**Where it shows up:**
- **Digital Arrest Shield** → tick *“Deep AI reasoning (Gemini)”* before analysing.
- **Citizen Fraud Shield** → every reply gains a *Gemini assistant* message,
  localised to the selected language.
- **Analyst API** → `POST /api/ai/ask` for a free-form command-centre copilot.
- Status endpoint: `GET /api/ai/status`.

Model defaults to `gemini-2.5-flash`; override with `GEMINI_MODEL` in `.env`.

---

## What makes it real (not a mock)

- **Trained ML model** — the scam detector is a genuine TF-IDF + Logistic Regression
  pipeline trained at boot on a labelled corpus, fused with a transparent rule engine.
- **Real computer vision** — the currency agent extracts actual image features
  (aspect ratio, colour distance, high-frequency micro-print energy, security-thread
  band, Laplacian sharpness). Upload *any* note image and watch it analyse.
- **Real graph analysis** — NetworkX community detection + PageRank on a live
  transaction graph produces the rings and roles you see.
- **Live database** — every scan, session, and alert is persisted (SQLModel) and
  reflected across the dashboard in real time.
- **Real-time bus** — a WebSocket pushes critical detections to the command center
  the instant they happen.

---

## Demo Script (2 minutes)

1. **Command Center** — open the dashboard; note the KPIs, 14-day trend, live feed.
2. **Digital Arrest Shield** — click the *Digital Arrest (CBI)* sample → **Analyse**.
   Watch it hit **CRITICAL 100%**, list the matched indicators, and fire a live alert
   (top banner + bottom-right toast) — reflecting how a real session would be flagged.
3. **Counterfeit Detection** — pick ₹500, upload any note image → **Verify**. See the
   per-feature security breakdown and verdict.
4. **Fraud Network Graph** — explore the force-directed money-movement graph; click a
   ring → generate & **export** its court-admissible intelligence package.
5. **Geo Intelligence** — pan the live India crime map; toggle hotspots vs incidents;
   read the patrol deployment queue.
6. **Citizen Fraud Shield** — tap an example or type a suspicious message; get an
   instant verdict, guided steps, and localised advisory (switch language).

---

## Project Structure

```
├── backend/                 # FastAPI + ML engines
│   ├── app/
│   │   ├── ml/              # scam_detector, currency_analyzer, fraud_graph, geo_intel, citizen_shield
│   │   ├── routers/        # scam, currency, fraud, geo, shield, dashboard, alerts (WS)
│   │   ├── data/           # labelled training corpus
│   │   ├── models.py       # SQLModel tables
│   │   ├── seed.py         # realistic demo data
│   │   └── main.py
│   └── requirements.txt
├── frontend/                # React + Vite + Tailwind command center
│   └── src/pages/          # Dashboard, Scam, Currency, Fraud, Geo, Shield
├── docs/ARCHITECTURE.md     # diagrams + design rationale
├── docker-compose.yml
└── start.sh
```

## Evaluation-Focus Mapping

| Evaluation criterion | Where it's addressed |
|---|---|
| Counterfeit detection accuracy across denominations & print quality | Per-denomination RBI profiles + 6-feature weighted scoring (`currency_analyzer.py`) |
| Digital-arrest detection precision & recall | Fused ML + rule model with balanced training corpus (`scam_detector.py`) |
| Fraud-network lead time before mass victimisation | Ring detection surfaces coordinated infrastructure early (`fraud_graph.py`) |
| False-positive rate for citizen tools (must be very low) | Conservative thresholds + genuine-message training + dual-signal fusion (`citizen_shield.py`) |
| Auditability of intelligence packages for legal admissibility | Named indicators, per-feature reports, timestamped transaction ledger (`intelligence_package`) |

---

<div align="center">
Built for the <b>AI for Digital Public Safety</b> challenge · National Cyber Crime Helpline <b>1930</b>
</div>
