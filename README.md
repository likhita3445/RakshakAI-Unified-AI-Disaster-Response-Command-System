# 🛡️ RakshakAI — Unified AI Disaster Response Command System

> **Fast, intelligent, multi-agency decision-support and tactical crisis command system.**

---

## 🌟 Key Features

- **🚨 AI Rescue Priority Score (0–100):** Real-time multi-criteria triage evaluating affected population, vulnerable groups (elderly, children, critical patients), route blockage hazards, and flood inundation crests.
- **🛣️ Dynamic Safe Rerouting Pathfinder:** Automatically detects submerged bridges/roads (Route A closed) and computes safe elevated bypasses (Route B Highland Bypass).
- **🎤 Multilingual Emergency Voice Parser:** Live Web Speech API (`hi-IN`, `en-IN`) entity extraction with smart offline voice dictation fallback.
- **⚡ Instant SOS Action Plan Generator:** Generates step-by-step rescue missions and optimal resource allocations (ALS Ambulances, NDRF Boats, Food/Water Airdrops) with zero latency.
- **🎮 Digital Twin "What-If" Simulator:** Real-time simulation of flood surges, population spikes, and bottleneck warnings.
- **🛰️ Drone & Satellite Computer Vision Recon:** Automated structural damage, submerged zone estimation, and rooftop victim cluster detection.
- **🔒 Multi-Agency Hub & Offline Cell Outage Sync:** Strict Role-Based Access Control (RBAC) across Police, NDRF, and Medical teams, local queue caching, and SHA-256 tamper-proof audit trails.

---

## 📂 Project Structure

```text
SIH 26 HACK/
├── ai/                      # AI Intelligence & Decision Support Layer
│   ├── prompts/             # Telemetry prompt templates (explain_prompt, fix_prompt)
│   ├── local_model.py       # Zero-dependency offline NLP & heuristic triage engine
│   └── model_provider.py    # Unified provider (Local/OpenAI/Gemini)
│
├── backend/                 # REST API Gateway (Flask)
│   ├── routes/              # Modular blueprints (analysis, fix, security)
│   ├── services/            # Core business logic services
│   ├── app.py               # Main Flask application entry point
│   └── requirements.txt     # Backend dependencies
│
├── database/                # Supabase & PostGIS GIS Engine
│   ├── database.sql         # Production PostgreSQL schema, PostGIS queries & RLS
│   └── schema.md            # ER diagrams, table definitions & stored procedures
│
├── docs/                    # Architecture & Documentation
│   ├── architecture.md      # Technical architecture with Mermaid topology
│   ├── workflow.md          # 2-Minute Judge Demo Guide & API Contracts
│   └── screenshots/         # Visual UI catalogue
│
├── frontend/                # Client Single-Page Application (SPA)
│   ├── index.html           # Main command portal
│   ├── combined.html        # Unified single-page command dashboard
│   ├── style.css            # Core glassmorphism design system
│   ├── dashboard.css        # Command center layout styles
│   ├── script.js            # Frontend orchestration & reactive state
│   └── api.js               # REST API service client
│
├── security/                # Security & Compliance Layer
│   ├── security_rules.py    # Multi-agency RBAC & SHA-256 audit logs
│   └── secret_detector.py   # Secret leak scanner & PII masking
│
├── tests/                   # Automated Test Suite (23/23 Passing)
│   ├── test_analysis.py     # AI triage & NLP unit tests
│   ├── test_fix.py          # Pathfinding & resource optimizer tests
│   ├── test_security.py     # Multi-agency RBAC & cryptographic tests
│   └── test_api.py          # End-to-end Flask REST API integration tests
│
├── requirements.txt         # Root Python dependencies
├── .gitignore               # Git ignore rules
└── LICENSE                  # MIT License
```

---

## 🚀 Quick Start Guide

### 1. Clone & Install Dependencies
```powershell
git clone <repo-url>
cd "SIH 26 HACK"
pip install -r requirements.txt
```

### 2. Launch Local Servers
```powershell
# Start Backend API (Port 5000)
cd backend
python app.py

# In another terminal, start Frontend Web Server (Port 3000)
cd ../frontend
python -m http.server 3000
```

### 3. Open in Browser
- **Unified Command Center:** http://localhost:3000/combined.html
- **Home & Live SOS:** http://localhost:3000/index.html

---

## 🧪 Running Automated Tests

```powershell
python -m unittest discover -s tests -p "test_*.py" -v
```
All **23 unit and integration tests** run in under 0.1s.

---

## 📜 License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
# 📸 RakshakAI — Visual UI & Screenshot Catalog

This directory contains visual captures and UI previews demonstrating RakshakAI in action.

---

### 🖼️ Core Interface Views

1. **`01_home_and_sos.png`**
   - Main landing view showing the emergency live alert ticker, unified header, and the **Multilingual AI Voice Report Parser**.
2. **`02_sos_action_plan_modal.png`**
   - Instant SOS Action Plan Generator modal with prioritized resources (Ambulances, NDRF boats, Water airdrop) and tactical dispatch sequence.
3. **`03_command_map_reroute.png`**
   - Interactive GIS command map showing Route A (submerged/closed) and dynamic rerouting to Route B (Highland Bypass).
4. **`04_explainability_why_modal.png`**
   - Mathematical explainability factor breakdown showing population weights, vulnerable counts, and route penalties.
5. **`05_digital_twin_simulator.png`**
   - Interactive flood depth slider, population multiplier, and real-time ambulance bottleneck alerts.
6. **`06_satellite_recon_ai.png`**
   - AI drone & satellite computer vision analysis detecting submerged structures and bridge collapse probability.
7. **`07_multi_agency_offline_hub.png`**
   - Multi-agency task dispatcher (NDRF, Police, Medical) with simulated cellular outage toggle and offline queue sync.
