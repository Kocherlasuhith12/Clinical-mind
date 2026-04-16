# ClinicalMind 🏥

> AI Diagnostic Support Co-Pilot for Rural Healthcare Workers in India

ClinicalMind helps ASHA workers and rural doctors in India get AI-assisted diagnostic support — in Tamil, Hindi, or English — even without internet connectivity.

---

## What It Does

- **Multimodal input** — describe symptoms via text, voice recording, or upload clinical images (skin, wounds, X-rays)
- **AI diagnosis** — GPT-4o Vision analyzes symptoms + images, produces differential diagnoses with confidence scores
- **RAG-grounded** — answers are cited against NHM India guidelines, RNTCP protocols, and PubMed
- **Emergency detection** — flags life-threatening cases immediately with 108 ambulance shortcut
- **Offline-first** — works without internet using ONNX local model; auto-syncs when reconnected
- **Multilingual** — Tamil, Hindi, English UI + voice transcription in all three languages
- **PDF export** — printable clinical case reports for patient records
- **Full audit trail** — every case, view, and export is logged for accountability

---

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | React 18 + Vite + Tailwind CSS + PWA |
| Backend | FastAPI + Python 3.11 |
| Auth | JWT (python-jose + bcrypt) |
| AI/LLM | OpenAI GPT-4o Vision + Whisper |
| RAG | LlamaIndex + Pinecone |
| Offline Model | ONNX Runtime |
| Job Queue | Celery + Redis |
| Database | PostgreSQL + SQLAlchemy |
| File Storage | Cloudflare R2 |
| Model Tracking | MLflow |
| Deployment | Docker + Docker Compose + Railway |

---

## Quick Start

### Prerequisites
- Docker + Docker Compose
- OpenAI API key
- Pinecone account (free tier works)
- Cloudflare R2 bucket (or use local storage for dev)

### 1. Clone and configure
```bash
git clone https://github.com/yourusername/clinicalmind
cd clinicalmind
cp backend/.env.example backend/.env
# Edit backend/.env with your API keys
```

### 2. Start all services
```bash
docker-compose up --build
```

This starts:
- FastAPI backend at `http://localhost:8000`
- React frontend at `http://localhost:5173`
- PostgreSQL at `localhost:5432`
- Redis at `localhost:6379`
- MLflow at `http://localhost:5000`
- Celery worker + beat scheduler

### 3. Ingest medical knowledge base
```bash
docker-compose exec backend python -m app.rag.ingest
```

### 4. Open the app
Visit `http://localhost:5173` → Register as a doctor or ASHA worker → Submit your first case.

---

## API Docs

Once running, visit:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

### Key endpoints

| Method | Route | Description |
|---|---|---|
| POST | `/auth/register` | Register user |
| POST | `/auth/login` | Get JWT token |
| GET  | `/auth/me` | Current user |
| POST | `/cases/submit` | Submit case (multipart) |
| GET  | `/cases/` | List my cases |
| GET  | `/cases/{id}` | Get case + diagnosis |
| GET  | `/cases/{id}/export` | Download PDF report |
| POST | `/cases/sync` | Sync offline cases |
| WS   | `/ws/cases/{id}/status` | Live diagnosis updates |

---

## Project Structure

```
clinicalmind/
├── backend/
│   ├── app/
│   │   ├── main.py              ← FastAPI app + WebSocket
│   │   ├── config.py            ← Settings from .env
│   │   ├── auth/                ← JWT + auth router
│   │   ├── cases/               ← Case submission, PDF export
│   │   ├── diagnosis/           ← Whisper, GPT-4o, ONNX pipeline
│   │   ├── rag/                 ← LlamaIndex + Pinecone
│   │   ├── alerts/              ← Emergency detection + SMS
│   │   ├── db/                  ← Models, migrations, session
│   │   └── tasks/               ← Celery workers
│   └── tests/
├── frontend/
│   └── src/
│       ├── pages/               ← Login, Register, Dashboard, NewCase, CaseResult
│       ├── components/          ← Navbar, DiagnosisCard, EmergencyBanner, etc.
│       ├── hooks/               ← useOfflineSync, useWebSocket, useAuthStore
│       ├── api/                 ← Axios client
│       └── i18n/                ← Tamil, Hindi, English translations
└── docker-compose.yml
```

---

## Deployment (Railway)

1. Push to GitHub
2. Create Railway project → Deploy from GitHub
3. Add services: PostgreSQL, Redis (Railway provides both)
4. Set environment variables from `.env.example`
5. Deploy — Railway auto-detects Dockerfile

---

## Ethical Note

ClinicalMind is a **clinical support tool**. It assists trained healthcare workers — it never replaces a doctor. Every diagnosis is clearly labelled as AI-generated and should be reviewed by qualified medical personnel before treatment decisions are made.

---

## Roadmap

- [ ] IndicASR integration for better Tamil/Hindi transcription
- [ ] Fine-tuned ONNX model on Indian clinical symptom data
- [ ] ABDM (Ayushman Bharat Digital Mission) integration
- [ ] Admin analytics dashboard
- [ ] Telemedicine video call integration
- [ ] WhatsApp bot interface for ASHA workers

---

## License

MIT — free to use, modify, and deploy for healthcare purposes.

Built with care for the 600M+ people in rural India who deserve better access to medical support.
