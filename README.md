# EchoAid

A personalized communication assistant for people with speech difficulties.

EchoAid lets patients communicate using large, customizable keyword buttons, saved phrases,
and text-to-speech. Guardians manage keywords, categories, and preferences through a
PIN-protected interface. An optional AI feature (powered by Groq) turns short word
fragments into full, speakable sentences.

---

## Phase Status

| Phase | Status | Description |
|---|---|---|
| 1 | ✅ Complete | Foundation, FastAPI backend, SQLite, visual shell |
| 2 | ✅ Complete | Guardian Dashboard — PIN auth, keyword & category CRUD |
| 3 | ✅ Complete | Patient communication interface + Web Speech API TTS |
| 4 | ✅ Complete | Groq AI-assisted sentence generation (Type & Speak) |
| 5 | ✅ Complete | Full test suite (75 tests), polish, documentation |

---

## Technology Stack

| Layer | Technology |
|---|---|
| Frontend | HTML5, CSS3, Vanilla JavaScript |
| Backend | Python 3.11+, FastAPI, Uvicorn |
| Validation | Pydantic v2 |
| Database | SQLAlchemy 2 + SQLite |
| Auth | JWT (python-jose) via HTTP-only cookie |
| Testing | Pytest + HTTPX TestClient |
| Font | Space Mono (Google Fonts — Monotonic) |
| TTS | Web Speech API (`SpeechSynthesis`) |
| AI | Groq API — OpenAI-compatible (`llama-3.1-8b-instant`) |

---

## Prerequisites

- Python 3.11 or later
- pip
- Internet access (Google Fonts CDN at runtime; Groq API for AI feature)

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

Edit `.env` and set at minimum:

| Variable | Required | Notes |
|---|---|---|
| `GUARDIAN_PIN` | Phase 2 | PIN to unlock Guardian Mode |
| `SECRET_KEY` | Phase 2 | Random string — generate with `python -c "import secrets; print(secrets.token_hex(32))"` |
| `AI_API_KEY` | Phase 4 (optional) | Groq API key from https://console.groq.com |

---

## Running the application

```bash
uvicorn backend.main:app --reload
```

Open **http://127.0.0.1:8000** in your browser.

| URL | Description |
|---|---|
| `/` | Mode selector (home) |
| `/patient` | Patient Mode — keywords, TTS, AI Type & Speak |
| `/guardian` | Guardian Mode — PIN login, keyword/category management |
| `/api/health` | Health check JSON |
| `/api/docs` | Interactive Swagger API docs |
| `/api/redoc` | ReDoc API docs |

The SQLite database (`echoaid.db`) is created automatically on first startup.

### First-time setup: Seed sample phrases

After the server starts, go to Guardian Mode → Sample Phrases → click **Seed Sample Phrases**.

This creates 5 starter categories (Urgent, Daily Needs, Health, Emotions, People)
with 27 pre-written phrases — all editable.

---

## Running tests

```bash
pytest tests/ -v
```

Tests use a temporary `test_echoaid.db` file that is wiped before and after each run.
Your development database is never touched.

**Test summary: 75 tests across 5 files.**

| File | Tests | What it covers |
|---|---|---|
| `test_health.py` | 15 | Health endpoint, pages, DB init, static assets |
| `test_auth.py` | 10 | PIN auth, cookies, protected endpoint guards |
| `test_categories.py` | 9 | Category CRUD, safe-delete, public/guardian access |
| `test_keywords.py` | 23 | Keyword CRUD, enable/disable, seed, preferences |
| `test_ai.py` | 18 | AI status, 503 when unconfigured, mocked calls, parsing |

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
│   ├── auth.py            # JWT session token helpers
│   ├── ai_service.py      # Groq API client + suggestion parsing
│   ├── main.py            # FastAPI app entry point
│   └── routers/
│       ├── health.py      # GET /api/health
│       ├── auth.py        # POST /api/auth/login|logout, GET /api/auth/check
│       ├── categories.py  # CRUD /api/categories/
│       ├── keywords.py    # CRUD /api/keywords/, POST /api/keywords/seed
│       ├── preferences.py # GET/PATCH /api/preferences/
│       └── ai.py          # GET /api/ai/status, POST /api/ai/suggest
├── frontend/
│   ├── index.html         # Mode selector
│   ├── patient.html       # Patient Mode (TTS + AI)
│   ├── guardian.html      # Guardian Mode (PIN + management)
│   ├── css/
│   │   ├── tokens.css     # Design tokens (Space Mono, color palette)
│   │   ├── base.css       # Reset + typography
│   │   ├── components.css # Buttons, cards, modals, toasts
│   │   └── layout.css     # Containers, grid, spacing, responsive utilities
│   └── js/
│       ├── app.js         # Shared: API wrapper, toasts, preferences, DOM helpers
│       ├── patient.js     # Patient Mode: TTS, category nav, AI suggestions
│       └── guardian.js    # Guardian Mode: auth, keyword/category CRUD
├── tests/
│   ├── conftest.py        # Session-scoped fixtures, DB setup/teardown
│   ├── test_health.py
│   ├── test_auth.py
│   ├── test_categories.py
│   ├── test_keywords.py
│   └── test_ai.py
├── .env.example
├── .gitignore
├── .gitattributes
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
| `APP_ENV` | `development` | `development` or `production` |
| `DATABASE_URL` | `sqlite:///./echoaid.db` | SQLAlchemy DB URL |
| `GUARDIAN_PIN` | `1234` | PIN for Guardian Mode — change this |
| `SECRET_KEY` | *(placeholder)* | JWT signing key — use a long random string |
| `SESSION_EXPIRE_MINUTES` | `480` | Session lifetime (8 hours) |
| `AI_PROVIDER_URL` | `https://api.groq.com/openai/v1` | Groq base URL |
| `AI_MODEL` | `llama-3.1-8b-instant` | Groq model name |
| `AI_API_KEY` | *(empty)* | Groq API key — get one free at console.groq.com |
| `AI_MAX_TOKENS` | `300` | Max tokens per suggestion response |
| `AI_TIMEOUT_SECONDS` | `15` | Groq request timeout |

---

## AI Feature (Groq)

EchoAid uses the [Groq API](https://console.groq.com) for AI sentence suggestions.

1. Get a free API key at https://console.groq.com
2. Set `AI_API_KEY=gsk_...` in your `.env`
3. Restart the server
4. The "Type & Speak" panel in Patient Mode will become active

**The AI feature is entirely optional.** All keyword-based communication works
without any AI configuration.

Supported models (set via `AI_MODEL`):
- `llama-3.1-8b-instant` — fast, good for short phrases (default)
- `llama-3.3-70b-versatile` — more capable, slightly slower
- `mixtral-8x7b-32768` — large context window

---

## Accessibility

- Semantic HTML5 + ARIA roles/labels throughout
- `aria-live` regions for dynamic announcements (screen readers)
- Keyboard-navigable with visible focus indicators (`box-shadow` focus ring)
- Minimum 48px touch targets on all interactive elements
- High-contrast mode toggle (CSS custom properties)
- Large-text mode toggle
- `prefers-reduced-motion` media query support
- Space Mono monospace font for consistent readability
- No color-alone status communication

Full WCAG 2.1 AA compliance requires a manual audit with assistive technologies.

---

## Security Limitations (Prototype Notice)

EchoAid is a local-device communication prototype.

- PIN-based guardian auth is suitable for single-device family use only.
- JWT tokens are signed but not encrypted; use HTTPS in any production deployment.
- SQLite is not suitable for multi-server or high-concurrency deployments.
- This application does not store, transmit, or process medical records.
- No warranty of fitness for any medical or clinical purpose is expressed or implied.

---

## License

MIT
