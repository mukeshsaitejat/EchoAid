# EchoAid

A personalized communication assistant for people with speech difficulties.

EchoAid lets patients communicate using large, customizable keyword buttons, saved phrases,
and text-to-speech. Guardians can manage keywords, categories, and preferences through a
separate PIN-protected interface.

---

## Phase Status

| Phase | Status | Description |
|---|---|---|
| 1 | ✅ Complete | Foundation, backend, database, visual shell |
| 2 | ⏳ Upcoming | Guardian Dashboard and keyword management |
| 3 | ⏳ Upcoming | Patient communication interface + TTS |
| 4 | ⏳ Upcoming | Optional AI-assisted sentence generation |
| 5 | ⏳ Upcoming | Testing, accessibility audit, deployment |

---

## Technology Stack

| Layer | Technology |
|---|---|
| Frontend | HTML5, CSS3, Vanilla JavaScript |
| Backend | Python 3.11+, FastAPI, Uvicorn |
| Validation | Pydantic v2 |
| Database | SQLAlchemy 2 + SQLite |
| Testing | Pytest + HTTPX TestClient |
| Font | Space Mono (Google Fonts — Monotonic) |
| TTS | Web Speech API (`SpeechSynthesis`) — Phase 3 |
| AI | OpenAI-compatible API (optional) — Phase 4 |

---

## Prerequisites

- Python 3.11 or later
- pip
- Internet access (for Google Fonts CDN at runtime; no build step required)

---

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/mukeshsaitejat/EchoAid.git
cd EchoAid
```

### 2. Create and activate a virtual environment

**Windows (PowerShell)**
```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

**macOS / Linux**
```bash
python -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

```bash
cp .env.example .env
```

Open `.env` and review the defaults. For Phase 1, the defaults work out of the box.
The `GUARDIAN_PIN` and `SECRET_KEY` fields are used in Phase 2.

---

## Running the application

```bash
uvicorn backend.main:app --reload
```

The server starts at **http://127.0.0.1:8000**.

| URL | Description |
|---|---|
| `http://127.0.0.1:8000/` | Mode selector (home) |
| `http://127.0.0.1:8000/patient` | Patient Mode |
| `http://127.0.0.1:8000/guardian` | Guardian Mode |
| `http://127.0.0.1:8000/api/health` | Health check (JSON) |
| `http://127.0.0.1:8000/api/docs` | Interactive API docs (Swagger UI) |
| `http://127.0.0.1:8000/api/redoc` | API docs (ReDoc) |

The SQLite database (`echoaid.db`) is created automatically on first startup.

---

## Running tests

```bash
pytest tests/ -v
```

Tests use an **in-memory SQLite database** and never modify your development database.

---

## Project Structure

```
EchoAid/
├── backend/
│   ├── __init__.py
│   ├── config.py          # Environment variable settings
│   ├── database.py        # SQLAlchemy engine + session
│   ├── models.py          # ORM models (Category, Keyword, Preferences)
│   ├── schemas.py         # Pydantic request/response schemas
│   ├── main.py            # FastAPI app, routers, static file serving
│   └── routers/
│       ├── __init__.py
│       └── health.py      # GET /api/health
├── frontend/
│   ├── index.html         # Mode selector
│   ├── patient.html       # Patient Mode
│   ├── guardian.html      # Guardian Mode
│   ├── css/
│   │   ├── tokens.css     # Design tokens (CSS custom properties)
│   │   ├── base.css       # Reset + typography
│   │   ├── components.css # Buttons, cards, badges, toasts, etc.
│   │   └── layout.css     # Containers, grid, spacing utilities
│   └── js/
│       ├── app.js         # Shared utilities: API, toasts, preferences
│       ├── patient.js     # Patient Mode logic (Phase 3)
│       └── guardian.js    # Guardian Mode logic (Phase 2)
├── tests/
│   ├── __init__.py
│   └── test_health.py     # Phase 1 backend tests
├── .env.example           # Environment variable template
├── .gitignore
├── requirements.txt
├── IMPLEMENTATION_PLAN.md
└── README.md
```

---

## Environment Variables

| Variable | Default | Description |
|---|---|---|
| `APP_HOST` | `127.0.0.1` | Uvicorn bind host |
| `APP_PORT` | `8000` | Uvicorn bind port |
| `APP_ENV` | `development` | Environment name |
| `DATABASE_URL` | `sqlite:///./echoaid.db` | SQLAlchemy database URL |
| `GUARDIAN_PIN` | `1234` | PIN for Guardian Mode (Phase 2) |
| `SECRET_KEY` | *(placeholder)* | Session token signing key (Phase 2) |
| `AI_PROVIDER_URL` | *(empty)* | OpenAI-compatible API base URL (Phase 4) |
| `AI_MODEL` | `gpt-4o-mini` | Model name (Phase 4) |
| `AI_API_KEY` | *(empty)* | AI provider API key — **keep secret** (Phase 4) |
| `AI_MAX_TOKENS` | `256` | Max tokens for AI responses (Phase 4) |
| `AI_TIMEOUT_SECONDS` | `15` | AI request timeout (Phase 4) |

---

## Security Limitations (Prototype Notice)

EchoAid is a local-device communication prototype, not a production medical application.

- PIN-based guardian access is appropriate for single-device family use only.
- SQLite is not suitable for multi-server or high-concurrency deployments.
- This application does not store, transmit, or process medical records.
- No warranty of fitness for any medical or clinical purpose is expressed or implied.
- For production deployment, replace SQLite with PostgreSQL and implement proper session management.

---

## Accessibility

EchoAid is designed with the following accessibility practices:

- Semantic HTML5 elements and ARIA roles/labels
- High-contrast mode toggle (CSS custom properties)
- Large-text mode toggle
- Keyboard-navigable interactions with visible focus indicators
- `aria-live` regions for dynamic announcements
- Minimum 48px touch targets
- Space Mono monospace font for readability
- Reduced-motion support via `@media (prefers-reduced-motion)`

Full WCAG 2.1 AA compliance requires a manual audit with assistive technologies.

---

## License

MIT
