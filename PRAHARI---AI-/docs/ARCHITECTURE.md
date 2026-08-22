# Prahari — System Architecture

**Prahari** (Sanskrit: *sentinel / guardian*) is an AI-powered Digital Public
Safety Intelligence platform that unifies five threat-neutralisation capabilities
into a single multi-agency command center — shifting law enforcement, banks, and
citizens from *reactive investigation* to *predictive threat neutralisation*.

## High-level architecture

```mermaid
flowchart TB
    subgraph Sources["📥 Multi-Source Intelligence Inputs"]
        A1["Telecom call / SMS /<br/>WhatsApp metadata"]
        A2["Note images<br/>(phone / PoS / counting machine)"]
        A3["Bank transaction &<br/>KYC / device metadata"]
        A4["Fraud complaints &<br/>seizure geolocations"]
        A5["Citizen queries<br/>(WhatsApp / IVR / app)"]
    end

    subgraph AI["🧠 AI Intelligence Engines (FastAPI)"]
        E1["Digital Arrest Detector<br/>TF-IDF + LogReg + rule fusion"]
        E2["Counterfeit CV Agent<br/>feature extraction + scoring"]
        E3["Fraud Graph Engine<br/>NetworkX community + PageRank"]
        E4["Geospatial Engine<br/>grid clustering + hotspot scoring"]
        E5["Citizen Shield<br/>NLP verdict + guided-action NLG"]
    end

    subgraph Core["⚙️ Platform Core"]
        DB[("SQLite / Postgres<br/>sessions · scans · accounts ·<br/>transactions · incidents · alerts")]
        WS["WebSocket Alert Bus<br/>/ws/alerts"]
        API["REST API<br/>/api/*"]
    end

    subgraph UI["🖥️ Command Center (React + Vite)"]
        U1["National Dashboard"]
        U2["Scam Console"]
        U3["Currency Scanner"]
        U4["Fraud Graph Explorer"]
        U5["Geo Intelligence Map"]
        U6["Citizen Shield Chat"]
    end

    A1 --> E1
    A2 --> E2
    A3 --> E3
    A4 --> E4
    A5 --> E5

    E1 --> DB
    E2 --> DB
    E3 --> DB
    E4 --> DB
    E5 --> API
    E1 -->|high/critical| WS

    DB --> API
    API --> UI
    WS -->|live alerts| UI

    E1 -.->|"telecom flag +<br/>victim warning"| Ext1["📞 Telecom / I4C / 1930"]
    E3 -.->|"court-admissible<br/>intelligence package"| Ext2["⚖️ Law Enforcement"]
```

## Data-flow: from contact to neutralisation

```mermaid
sequenceDiagram
    participant C as Scam Caller
    participant T as Telecom / Session
    participant P as Prahari Engine
    participant CC as Command Center
    participant V as Potential Victim

    C->>T: "You are under digital arrest…"
    T->>P: POST /api/scam/analyze (transcript, caller-id)
    P->>P: TF-IDF model + rule indicators → fused risk
    alt risk ≥ 0.85 (critical)
        P->>CC: WebSocket alert (block & intercept)
        P->>V: In-call safety advisory + throttle payment
        P->>T: Flag caller-ID to telecom
    else risk 0.60–0.85 (high)
        P->>CC: Analyst review queue + subscriber warning
    end
    Note over P,CC: All verdicts logged with named indicators<br/>for auditability & legal admissibility
```

## Module design

| Module | Technique | Why it works |
|---|---|---|
| **Digital Arrest Detection** | TF-IDF (1–2 gram) + Logistic Regression trained on labelled scam/legit corpus, fused with a weighted rule layer of 10 named indicator families | Data-driven generalisation *plus* transparent, explainable evidence for every alert (audit requirement). Rules catch novel scripts the model hasn't seen. |
| **Counterfeit Currency Agent** | Pillow/NumPy feature extraction — aspect ratio, dominant colour vs RBI profile, micro-print via high-frequency energy, security-thread band detection, Laplacian sharpness, RBI serial regex | Runs on-device (no GPU), works across all 7 denominations, returns a **per-feature** breakdown a field officer can trust and defend. |
| **Fraud Network Graph** | Directed money-flow graph + shared device/phone linkage, greedy-modularity community detection, PageRank centrality for role inference (kingpin/mule/layer) | Surfaces coordinated rings *before* mass victimisation; auto-generates court-admissible evidence packages traceable to source transactions. |
| **Geospatial Intelligence** | Grid-based spatial clustering (~5.5 km cells), intensity scoring, state-level rollups | Patrol prioritisation, resource deployment, inter-district intelligence sharing — near real-time. |
| **Citizen Fraud Shield** | Reuses the scam NLP verdict, wrapped in guided-action NLG, 1930/NCRB reporting pathway, advisory in 12 Indian languages | Very low false-positive tuning; meets citizens where they are (WhatsApp/IVR/app). |

## Technology stack

- **Backend:** FastAPI, SQLModel (SQLite → Postgres-ready), scikit-learn, NumPy, Pillow, NetworkX, WebSockets
- **Frontend:** React 18, Vite, TailwindCSS, Recharts, Leaflet, react-force-graph
- **Delivery:** Docker Compose (backend + nginx-served SPA), or one-command `./start.sh`

## Auditability & legal admissibility

Every intelligence output is designed to survive scrutiny:
- Scam verdicts carry the **exact matched phrases** and both model + rule scores.
- Currency verdicts list **each security feature** with pass/fail and measured value.
- Fraud packages include a **transaction ledger** where every graph edge maps to a
  timestamped source record, with a chain-of-custody note aligned to BNSS / IT Act.
