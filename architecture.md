# 🛡️ RakshakAI — System Architecture Document

## 1. System Overview

**RakshakAI** is an advanced, unified AI decision-support and emergency command platform for disaster response and crisis management. It moves beyond passive monitoring by dynamically computing **multi-factor triage priority scores**, generating **instant step-by-step rescue plans**, performing **safe road pathfinding bypasses around submerged infrastructure**, and synchronizing **multi-agency dispatches** across online and offline environments.

---

## 2. High-Level Architecture Diagram

```mermaid
graph TD
    subgraph ClientLayer ["🖥️ Client Layer (Frontend SPA)"]
        UI_Home["🏠 Home & Live SOS Portal"]
        UI_Dash["🚨 Command Center (Leaflet GIS)"]
        UI_Twin["🎮 Digital Twin Simulator & Satellite AI"]
        UI_Sec["🔒 Multi-Agency Hub & Offline Queue"]
        VoiceEngine["🎤 Web Speech API & Voice Dictation Fallback"]
    end

    subgraph APILayer ["⚡ REST API Gateway (Flask)"]
        HealthRoute["GET /api/health"]
        AnalysisRoutes["POST /api/analysis/priority<br/>POST /api/analysis/nlp<br/>POST /api/analysis/simulate"]
        FixRoutes["POST /api/fix/action-plan<br/>POST /api/fix/reroute<br/>POST /api/fix/allocate"]
        SecurityRoutes["POST /api/security/dispatch<br/>POST /api/security/sync-offline<br/>GET /api/security/explain/:id"]
    end

    subgraph AILayer ["🧠 AI Intelligence & Decision Layer"]
        ModelProvider["Unified Model Provider Layer"]
        LocalModel["Local Disaster Model (Zero-Latency)"]
        ExplainEngine["Decision Math Explainability Engine"]
        NLPParser["Multilingual Emergency Entity Parser"]
        Prompts["Prompt Templates (explain_prompt / fix_prompt)"]
    end

    subgraph SecurityLayer ["🔒 Security & Multi-Agency Governance"]
        RBAC["Role-Based Access Control (Clearance Levels 1-5)"]
        Sanitizer["XSS & Input Sanitizer"]
        SecretScanner["Secret & PII Detector"]
        AuditChain["Tamper-Proof SHA-256 Audit Log Chain"]
    end

    subgraph FieldAgencies ["🚑 Multi-Agency Field Coordination"]
        NDRF["NDRF Boat Squads"]
        Police["Traffic Police Rerouting"]
        Medical["ALS Ambulances & Triage"]
        SDRF["SDRF Logistics & Supplies"]
    end

    ClientLayer -->|HTTP / JSON (Port 3000 -> 5000)| APILayer
    APILayer --> AILayer
    APILayer --> SecurityLayer
    SecurityLayer --> FieldAgencies
    AILayer --> FixRoutes
```

---

## 3. Core Component Subsystems

### 3.1. Client Layer (`frontend/`)
- **Single Page Application (SPA):** Built with Vanilla HTML5, modern CSS3 (glassmorphism design system), and responsive view routing.
- **Interactive GIS Map:** Leaflet.js with dynamic SVG polylines for primary (blocked), highland bypass (recommended), and boat rescue channels.
- **Voice Recognition & Regional NLP:** Real-time Web Speech API (`hi-IN`, `en-IN`) with smart fallback dictation simulation when offline or operating under `file://` protocols.

### 3.2. REST Backend Layer (`backend/`)
- **Flask Framework:** Modular blueprint architecture with separation of concerns:
  - `routes/analysis_routes.py`: Priority calculations, NLP entity extraction, digital twin simulations.
  - `routes/fix_routes.py`: SOS rescue action plans, dynamic reroute pathfinding, supply optimization.
  - `routes/security_routes.py`: Multi-agency dispatch logs, offline sync queue, explainability.

### 3.3. AI Intelligence Engine (`ai/`)
- **Dual Architecture:** Plug-and-play support for cloud LLMs (OpenAI, Gemini) with a built-in **100% offline heuristic & neural rule engine (`LocalDisasterModel`)** ensuring zero downtime during cellular/satellite outages.
- **Prompt Engineering (`ai/prompts/`):** Standardized disaster telemetry prompt templates for decision rationale and resource allocation.

### 3.4. Security & Compliance Layer (`security/`)
- **RBAC Matrix:** Strict multi-agency permission enforcement across 6 role tiers.
- **Secret & PII Scanner:** Continuous regex scanner protecting against exposed API credentials and citizen identities in public dispatch streams.
- **Cryptographic Audit Log:** SHA-256 blockchain-style hashing of every action and dispatch for post-crisis legal/judicial review.

---

## 4. Priority Scoring Mathematical Formula

The **RakshakAI Priority Score (0–100)** is computed using multi-criteria weighted decision analysis:

$$\text{Priority Score} = P_{\text{pop}} + V_{\text{vuln}} + M_{\text{med}} + R_{\text{route}} + F_{\text{flood}}$$

Where:
- **$P_{\text{pop}}$ (Max 30 pts):** Population exposure factor $=\min\left(30, \left\lfloor\frac{\text{Affected}}{1000} \times 30\right\rfloor\right)$
- **$V_{\text{vuln}}$ (Max 25 pts):** Vulnerable demographics factor $= \min(25, \lfloor(1.5 \cdot \text{Critical} + 0.3 \cdot \text{Elderly} + 0.2 \cdot \text{Children} + 0.4 \cdot \text{Disabled}) \times 1.2\rfloor)$
- **$M_{\text{med}}$ (15 pts):** Immediate medical/trauma crisis flag (15 pts if active, else 0)
- **$R_{\text{route}}$ (Max 16 pts):** Road inaccessibility hazard index (16 pts if primary bridge blocked, else 8)
- **$F_{\text{flood}}$ (Max 14 pts):** Inundation crest factor $= \left\lfloor\frac{\text{Flood Level (\%)}}{100} \times 14\right\rfloor$
