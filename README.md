<div align="center">

<img src="https://img.shields.io/badge/ClinicalMind-AI%20Diagnostic%20Co--Pilot-0ea5e9?style=for-the-badge&logo=heart&logoColor=white" alt="ClinicalMind" height="40"/>

# ClinicalMind 🏥
 
### AI Diagnostic Support Co-Pilot for Rural Healthcare Workers in India  
 
*Bridging the medical access gap for 600M+ people — offline-first, multilingual, and built for the field.*
 
<br/>

[![FastAPI](https://img.shields.io/badge/FastAPI-0.110-009688?style=flat-square&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-18-61DAFB?style=flat-square&logo=react&logoColor=black)](https://react.dev/)
[![Python](https://img.shields.io/badge/Python-3.11-3776AB?style=flat-square&logo=python&logoColor=white)](https://python.org/)
[![GPT-4o](https://img.shields.io/badge/GPT--4o-Vision-412991?style=flat-square&logo=openai&logoColor=white)](https://openai.com/)
[![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?style=flat-square&logo=docker&logoColor=white)](https://docker.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green?style=flat-square)](./LICENSE)
[![PWA](https://img.shields.io/badge/PWA-Offline--First-5A0FC8?style=flat-square&logo=pwa&logoColor=white)](https://web.dev/progressive-web-apps/)

<br/>

[**Live Demo**](#) · [**API Docs**](http://localhost:8000/docs) · [**Report a Bug**](../../issues) · [**Request Feature**](../../issues)

<br/>

> **⚕️ Disclaimer:** ClinicalMind is a clinical *support* tool. Every AI-generated diagnosis must be reviewed by a qualified healthcare professional before any treatment decision is made.

</div>

---

## 📋 Table of Contents

- [Overview](#-overview)
- [Key Features](#-key-features)
- [System Architecture](#-system-architecture)
- [Tech Stack](#-tech-stack)
- [Getting Started](#-getting-started)
- [Project Structure](#-project-structure)
- [API Reference](#-api-reference)
- [Offline Functionality](#-offline-functionality)
- [Multilingual Support](#-multilingual-support)
- [Deployment](#-deployment)
- [Roadmap](#-roadmap)
- [Contributing](#-contributing)
- [License](#-license)

---

## 🌍 Overview

India has **1 doctor per 1,456 people** in rural areas — far below the WHO standard of 1 per 1,000. ASHA workers and rural practitioners often make critical triage decisions without specialist access, diagnostic tools, or reliable connectivity.

**ClinicalMind** is an offline-first AI diagnostic co-pilot built specifically for this reality. Healthcare workers can describe symptoms via text or voice, upload clinical images, and receive GPT-4o–powered differential diagnoses grounded in NHM India guidelines and RNTCP protocols — even with zero internet.

```
ASHA Worker in rural Tamil Nadu
        │
        │  (offline, no connectivity)
        ▼
┌─────────────────────┐
│   ClinicalMind PWA  │  ← Tamil voice input + image upload
│   (ONNX local model)│  ← Runs fully on-device
│                     │  ← Flags emergencies → 108 shortcut
└─────────┬───────────┘
          │  (reconnects to internet)
          ▼
┌─────────────────────┐
│  FastAPI + GPT-4o   │  ← Full RAG-grounded diagnosis
│  LlamaIndex+Pinecone│  ← Cited against medical guidelines
│  Celery + Redis     │  ← Async job processing
└─────────────────────┘
```

---

## ✨ Key Features

### 🔬 AI-Powered Diagnostics
- **Multimodal input** — symptoms via text, voice recording, or clinical image upload (skin, wounds, X-rays)
- **Differential diagnosis** — GPT-4o Vision returns ranked diagnoses with confidence scores and reasoning
- **RAG-grounded answers** — every response cited against NHM India guidelines, RNTCP TB protocols, and PubMed literature
- **WebSocket live updates** — real-time diagnosis status pushed to the client as Celery tasks complete

### 🚨 Emergency Detection
- Automatic life-threatening case flagging with prominent UI alerts
- One-tap **108 ambulance shortcut** surfaced immediately on emergency detection
- SMS alerts via integrated notification pipeline

### 📴 Offline-First Architecture
- Full diagnostic capability **without internet** using a quantized ONNX local model
- PWA caching with service workers for all UI assets and recent case data
- Automatic queue-and-sync — offline cases submitted to the server when connectivity returns
- Sync status indicator always visible in the UI

### 🗣️ Multilingual Support
- Complete UI in **Tamil**, **Hindi**, and **English**
- Voice transcription in all three languages via OpenAI Whisper
- Roadmap: IndicASR for improved accuracy on regional accents

### 📄 Clinical Records & Audit
- PDF export of complete clinical case reports — printable for physical patient files
- Full audit trail on every case view, submission, and export
- MLflow model tracking for diagnostic performance over time

---

## 🏗️ System Architecture

```
┌──────────────────────────────────────────────────────────────────┐
│                        CLIENT LAYER                              │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │              React 18 + Vite PWA (Tailwind CSS)          │   │
│  │                                                          │   │
│  │  ┌────────────┐  ┌───────────┐  ┌────────────────────┐  │   │
│  │  │  i18n UI   │  │  Voice    │  │  Offline Sync Hook │  │   │
│  │  │ Tamil/Hindi│  │ Recording │  │  (IndexedDB queue) │  │   │
│  │  └────────────┘  └───────────┘  └────────────────────┘  │   │
│  │                                                          │   │
│  │  ┌───────────────────────────────────────────────────┐  │   │
│  │  │           ONNX Local Model (offline mode)         │  │   │
│  │  └───────────────────────────────────────────────────┘  │   │
│  └──────────────────────────────────────────────────────────┘   │
└────────────────────────────┬─────────────────────────────────────┘
                             │ HTTPS / WebSocket
┌────────────────────────────▼─────────────────────────────────────┐
│                        API LAYER                                 │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │                 FastAPI + Python 3.11                    │   │
│  │                                                          │   │
│  │  /auth   /cases   /cases/{id}/export   /ws/cases/{id}   │   │
│  │                  JWT (python-jose)                       │   │
│  └──────────┬───────────────────┬───────────────────────────┘   │
│             │                   │                                │
│  ┌──────────▼──────┐   ┌────────▼───────────────────────────┐  │
│  │  Celery + Redis │   │        Diagnosis Pipeline          │  │
│  │  (async jobs)   │   │                                    │  │
│  │                 │   │  1. Whisper (audio transcription)  │  │
│  │  celery beat    │   │  2. GPT-4o Vision (diagnosis)      │  │
│  │  (scheduler)    │   │  3. LlamaIndex + Pinecone (RAG)    │  │
│  └─────────────────┘   │  4. Emergency detection            │  │
│                        │  5. PDF generation                 │  │
│                        └────────────────────────────────────┘  │
└──────────────────────────────┬───────────────────────────────────┘
                               │
┌──────────────────────────────▼───────────────────────────────────┐
│                       DATA LAYER                                 │
│                                                                  │
│  ┌──────────────┐  ┌─────────────┐  ┌──────────┐  ┌─────────┐  │
│  │  PostgreSQL  │  │  Pinecone   │  │  CF R2   │  │ MLflow  │  │
│  │ (SQLAlchemy) │  │ (vector DB) │  │ (images) │  │ (model  │  │
│  │              │  │             │  │          │  │ tracks) │  │
│  └──────────────┘  └─────────────┘  └──────────┘  └─────────┘  │
└──────────────────────────────────────────────────────────────────┘
```

---

## 🛠️ Tech Stack

| Layer | Technology | Purpose |
|---|---|---|
| **Frontend** | React 18 + Vite + Tailwind CSS | UI framework |
| **PWA** | Workbox Service Worker | Offline caching & install |
| **Auth** | JWT · python-jose · bcrypt | Stateless auth |
| **Backend** | FastAPI + Python 3.11 | REST API + WebSocket |
| **AI / Vision** | OpenAI GPT-4o Vision | Multimodal diagnosis |
| **Speech** | OpenAI Whisper | Voice transcription |
| **RAG** | LlamaIndex + Pinecone | Retrieval-augmented grounding |
| **Offline Model** | ONNX Runtime | On-device inference |
| **Job Queue** | Celery + Redis | Async task processing |
| **Database** | PostgreSQL + SQLAlchemy | Relational persistence |
| **File Storage** | Cloudflare R2 | Image / PDF storage |
| **Model Tracking** | MLflow | Experiment & performance tracking |
| **Deployment** | Docker + Docker Compose + Railway | Containerised deployment |
| **i18n** | react-i18next | Tamil · Hindi · English |

---

## 🚀 Getting Started

### Prerequisites

| Requirement | Version |
|---|---|
| Docker + Docker Compose | Latest |
| OpenAI API Key | GPT-4o + Whisper access |
| Pinecone Account | Free tier works |
| Cloudflare R2 Bucket | Or use local storage for dev |

### 1. Clone & Configure

```bash
git clone https://github.com/yourusername/clinicalmind
cd clinicalmind
cp backend/.env.example backend/.env
```

Open `backend/.env` and fill in your secrets:

```env
# OpenAI
OPENAI_API_KEY=sk-...

# Pinecone
PINECONE_API_KEY=...
PINECONE_ENVIRONMENT=...
PINECONE_INDEX_NAME=clinicalmind

# Cloudflare R2
R2_ACCOUNT_ID=...
R2_ACCESS_KEY_ID=...
R2_SECRET_ACCESS_KEY=...
R2_BUCKET_NAME=clinicalmind-files

# Database
DATABASE_URL=postgresql://postgres:password@db:5432/clinicalmind

# Redis
REDIS_URL=redis://redis:6379/0

# JWT
SECRET_KEY=your-super-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440
```

### 2. Start All Services

```bash
docker-compose up --build
```

This starts:

| Service | URL |
|---|---|
| React Frontend | http://localhost:5173 |
| FastAPI Backend | http://localhost:8000 |
| Swagger Docs | http://localhost:8000/docs |
| PostgreSQL | localhost:5432 |
| Redis | localhost:6379 |
| MLflow UI | http://localhost:5000 |
| Celery Worker | (background) |
| Celery Beat | (background scheduler) |

### 3. Ingest Medical Knowledge Base

```bash
docker-compose exec backend python -m app.rag.ingest
```

This indexes NHM India guidelines, RNTCP TB protocols, and curated PubMed abstracts into Pinecone for RAG retrieval.

### 4. Register & Submit Your First Case

1. Visit **http://localhost:5173**
2. Register as a **Doctor** or **ASHA Worker**
3. Navigate to **New Case** → describe symptoms (text or voice)
4. Optionally upload a clinical image
5. Submit → watch the live diagnosis stream in via WebSocket

---

## 📁 Project Structure

```
clinicalmind/
│
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI app entry point + WebSocket router
│   │   ├── config.py            # Pydantic Settings — loads from .env
│   │   │
│   │   ├── auth/
│   │   │   ├── router.py        # /auth/register, /auth/login, /auth/me
│   │   │   ├── models.py        # User SQLAlchemy model
│   │   │   ├── schemas.py       # Pydantic request/response schemas
│   │   │   └── utils.py         # JWT creation, bcrypt hashing
│   │   │
│   │   ├── cases/
│   │   │   ├── router.py        # /cases CRUD + /cases/{id}/export
│   │   │   ├── models.py        # Case, Diagnosis SQLAlchemy models
│   │   │   ├── schemas.py       # Case submission + result schemas
│   │   │   └── pdf.py           # ReportLab PDF generation
│   │   │
│   │   ├── diagnosis/
│   │   │   ├── pipeline.py      # Orchestrates Whisper → GPT-4o → RAG
│   │   │   ├── whisper.py       # Audio transcription (Tamil/Hindi/English)
│   │   │   ├── gpt4o.py         # GPT-4o Vision differential diagnosis
│   │   │   └── onnx.py          # Offline ONNX inference fallback
│   │   │
│   │   ├── rag/
│   │   │   ├── ingest.py        # PDF/text ingestion → Pinecone index
│   │   │   └── retriever.py     # LlamaIndex query engine
│   │   │
│   │   ├── alerts/
│   │   │   ├── detector.py      # Emergency keyword + confidence threshold logic
│   │   │   └── sms.py           # SMS alert integration
│   │   │
│   │   ├── db/
│   │   │   ├── base.py          # SQLAlchemy declarative base
│   │   │   ├── session.py       # DB session dependency
│   │   │   └── migrations/      # Alembic migration scripts
│   │   │
│   │   └── tasks/
│   │       ├── celery_app.py    # Celery app + Redis broker config
│   │       └── diagnosis.py     # Async diagnosis Celery task
│   │
│   ├── tests/
│   │   ├── test_auth.py
│   │   ├── test_cases.py
│   │   └── test_diagnosis.py
│   │
│   ├── Dockerfile
│   └── requirements.txt
│
├── frontend/
│   └── src/
│       ├── pages/
│       │   ├── Login.jsx
│       │   ├── Register.jsx
│       │   ├── Dashboard.jsx    # Case list + workflow count
│       │   ├── NewCase.jsx      # Symptom input + image upload
│       │   └── CaseResult.jsx   # Live diagnosis + PDF export
│       │
│       ├── components/
│       │   ├── Navbar.jsx
│       │   ├── DiagnosisCard.jsx      # Differential with confidence bars
│       │   ├── EmergencyBanner.jsx    # 108 shortcut + alert UI
│       │   ├── VoiceRecorder.jsx      # MediaRecorder + Whisper upload
│       │   ├── ImageUploader.jsx      # Drag-and-drop clinical images
│       │   └── SyncIndicator.jsx      # Online/offline sync status
│       │
│       ├── hooks/
│       │   ├── useOfflineSync.js      # IndexedDB queue + sync logic
│       │   ├── useWebSocket.js        # Live diagnosis status subscription
│       │   └── useAuthStore.js        # Zustand auth state
│       │
│       ├── api/
│       │   └── client.js              # Axios instance + interceptors
│       │
│       └── i18n/
│           ├── en.json
│           ├── hi.json
│           └── ta.json
│
├── docker-compose.yml
└── README.md
```

---

## 📡 API Reference

Full interactive documentation available at `http://localhost:8000/docs` (Swagger UI) and `http://localhost:8000/redoc`.

### Authentication

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/auth/register` | Register as doctor or ASHA worker |
| `POST` | `/auth/login` | Obtain JWT access token |
| `GET` | `/auth/me` | Get current authenticated user |

### Cases

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/cases/submit` | Submit new case (multipart: text + audio + images) |
| `GET` | `/cases/` | List all cases for current user |
| `GET` | `/cases/{id}` | Retrieve case + full diagnosis result |
| `GET` | `/cases/{id}/export` | Download printable PDF clinical report |
| `POST` | `/cases/sync` | Batch-sync offline-queued cases |

### Real-time

| Protocol | Endpoint | Description |
|---|---|---|
| `WS` | `/ws/cases/{id}/status` | Live diagnosis progress updates |

### Example: Submit a Case

```bash
curl -X POST http://localhost:8000/cases/submit \
  -H "Authorization: Bearer <your_jwt>" \
  -F "symptoms=Patient presents with persistent cough for 3 weeks, night sweats, weight loss" \
  -F "language=en" \
  -F "image=@xray.jpg"
```

**Response:**

```json
{
  "case_id": "c7f3a1b2-...",
  "status": "processing",
  "ws_url": "/ws/cases/c7f3a1b2-.../status"
}
```

---

## 📴 Offline Functionality

ClinicalMind is designed to work in areas with zero connectivity.

```
Online Mode                         Offline Mode
─────────────────────────────       ────────────────────────────────
GPT-4o Vision via API          →    Quantized ONNX model (on-device)
LlamaIndex + Pinecone RAG      →    Cached guidelines (IndexedDB)
Real-time WebSocket updates    →    Local processing, no WS needed
Server-side PDF export         →    Client-side PDF generation
```

**How offline sync works:**

1. Cases submitted offline are stored in **IndexedDB** with `status: queued`
2. A `useOfflineSync` hook listens for the browser's `online` event
3. On reconnect, queued cases are batch-posted to `/cases/sync`
4. Server processes them through the full GPT-4o pipeline
5. Results are pushed back to the client and cached

---

## 🌐 Multilingual Support

| Language | UI | Voice Input | AI Response |
|---|---|---|---|
| English | ✅ | ✅ Whisper | ✅ |
| Hindi | ✅ | ✅ Whisper | ✅ |
| Tamil | ✅ | ✅ Whisper | ✅ |

Language is auto-detected from the user's profile preference and can be switched at any time via the language toggle in the navbar. The GPT-4o system prompt is dynamically constructed to respond in the selected language.

---

## 🚢 Deployment

### Railway (Recommended)

1. Push your repository to GitHub
2. Create a new **Railway project** → **Deploy from GitHub repo**
3. Add managed services: **PostgreSQL** and **Redis** (Railway provides both natively)
4. Set all environment variables from `backend/.env.example` in the Railway dashboard
5. Railway auto-detects the `Dockerfile` and builds on every push to `main`

### Environment Variables Reference

```env
# Required for production
OPENAI_API_KEY=
PINECONE_API_KEY=
PINECONE_ENVIRONMENT=
PINECONE_INDEX_NAME=
R2_ACCOUNT_ID=
R2_ACCESS_KEY_ID=
R2_SECRET_ACCESS_KEY=
R2_BUCKET_NAME=
DATABASE_URL=
REDIS_URL=
SECRET_KEY=
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440

# Optional
MLFLOW_TRACKING_URI=
SENTRY_DSN=
SMS_API_KEY=
```

### Docker Production Build

```bash
# Build production images
docker-compose -f docker-compose.prod.yml up --build -d

# Run DB migrations
docker-compose exec backend alembic upgrade head

# Ingest knowledge base
docker-compose exec backend python -m app.rag.ingest
```

---

## 🗺️ Roadmap

| Status | Feature |
|---|---|
| 🔄 In Progress | IndicASR integration for Tamil/Hindi accent accuracy |
| 📋 Planned | Fine-tuned ONNX model on Indian clinical symptom datasets |
| 📋 Planned | ABDM (Ayushman Bharat Digital Mission) patient record integration |
| 📋 Planned | Admin analytics dashboard (case volume, diagnosis accuracy, flagged emergencies) |
| 📋 Planned | Telemedicine video call integration for specialist consults |
| 📋 Planned | WhatsApp bot interface — zero-app-install access for ASHA workers |
| 💡 Exploring | Federated learning for privacy-preserving model improvement |
| 💡 Exploring | Voice-only interface for low-literacy users |

---

## 🤝 Contributing

Contributions are welcome — especially from healthcare professionals who can validate clinical logic, and engineers familiar with low-resource deployment environments.

```bash
# Fork the repo, then:
git checkout -b feature/your-feature-name
git commit -m "feat: describe your change"
git push origin feature/your-feature-name
# Open a Pull Request
```

Please read `CONTRIBUTING.md` before submitting. For major changes, open an issue first to discuss the approach.

---

## ⚖️ Ethical Commitment

ClinicalMind operates under strict ethical principles:

- **AI assists, doctors decide** — every diagnosis is clearly labelled AI-generated and must be reviewed by a qualified professional
- **No data monetisation** — patient case data is never used for commercial purposes
- **Audit trail** — every case, view, and export is logged for accountability and quality review
- **Transparency** — confidence scores and source citations are always shown, never hidden
- **Open source** — the full codebase is available for scrutiny and community improvement

---

## 📄 License

MIT License — free to use, modify, and deploy for healthcare and research purposes.

See [LICENSE](./LICENSE) for full terms.

---

<div align="center">

Built with care for the **600 million people in rural India** who deserve better access to medical support.

<br/>

**If this project helps even one ASHA worker make a better call in the field, it's worth building.**

<br/>

⭐ **Star this repo** if you believe technology can help close the healthcare access gap.

</div>
