# EchoAid — Implementation Plan

EchoAid is a personalized communication assistant for people with speech difficulties.
It provides customized keyword buttons, saved phrases, text-to-speech, and optional AI assistance.

---

## Project Structure

```
EchoAid/
├── backend/
│   ├── main.py               # FastAPI application entry point
│   ├── database.py           # SQLAlchemy engine and session setup
│   ├── models.py             # SQLAlchemy ORM models
│   ├── schemas.py            # Pydantic request/response schemas
│   ├── routers/
│   │   ├── health.py         # Health-check endpoint
│   │   ├── categories.py     # Category CRUD (Phase 2+)
│   │   └── keywords.py       # Keyword CRUD (Phase 2+)
│   └── config.py             # Environment variable configuration
├── frontend/
│   ├── index.html            # Application shell / mode selector
│   ├── patient.html          # Patient Mode screen (Phase 3)
│   ├── guardian.html         # Guardian Mode screen (Phase 2)
│   ├── css/
│   │   ├── tokens.css        # Design tokens (CSS custom properties)
│   │   ├── base.css          # Reset, typography, global styles
│   │   ├── components.css    # Reusable components (buttons, cards, etc.)
│   │   └── layout.css        # Page-level layout
│   └── js/
│       ├── app.js            # Shared app utilities
│       ├── patient.js        # Patient Mode logic (Phase 3)
│       └── guardian.js       # Guardian Mode logic (Phase 2)
├── tests/
│   └── test_health.py        # Phase 1 backend tests
├── .env.example              # Environment variable template
├── .gitignore
├── requirements.txt
├── README.md
└── IMPLEMENTATION_PLAN.md
```

---

## Phase 1 — Foundation and Visual Shell

**Goal:** Establish the working project skeleton with a polished, responsive interface shell.

### Requirements
1. Inspect existing workspace before changes — preserve useful files.
2. Establish the FastAPI application.
3. Serve frontend files from the backend (single origin).
4. Establish SQLite database connection and SQLAlchemy configuration.
5. Prepare Category and Keyword database models.
6. Initialize the database safely (idempotent `create_all`).
7. Add configurable environment variables via `.env` / `python-dotenv`.
8. Create a professional, responsive interface shell.
9. Establish Patient Mode and Guardian Mode navigation/entry points.
10. Create visual foundations and placeholder screens.
11. Add `/health` endpoint.
12. Document setup, installation, and execution.
13. Add `.gitignore` and `.env.example`.

### Acceptance Criteria
- [x] Backend starts without errors.
- [x] Homepage loads through FastAPI at `http://localhost:8000`.
- [x] Static assets (CSS, JS) are served correctly.
- [x] `/health` endpoint returns `{"status": "ok"}`.
- [x] Database initializes idempotently.
- [x] Application shell is responsive (desktop, tablet, mobile).
- [x] No real API keys or secrets are committed.
- [x] Setup instructions in README are accurate.

**Phase 1 complete — 15/15 tests passing.**

---

## Phase 2 — Guardian Dashboard

**Goal:** Implement Guardian Mode with PIN authentication and full keyword management.

### Requirements
1. PIN-based guardian access (PIN from environment variable).
2. Backend-managed authenticated session (HTTP-only cookie or signed token).
3. Protect all keyword-management API routes.
4. CRUD for keywords: create, read, update, delete, enable/disable, reorder.
5. CRUD for categories (with safe-delete guardrails).
6. Urgency flags on keywords.
7. Optional icon/symbol association.
8. Input validation via Pydantic.
9. Seed sample phrases (consent/autonomy phrases included).
10. Clear success and error feedback in the UI.

### Acceptance Criteria
- [ ] Unauthenticated requests to guardian routes return 401/403.
- [ ] PIN entry grants authenticated session.
- [ ] Guardian can create, edit, delete, enable/disable, reorder keywords.
- [ ] Guardian can create, edit, delete categories (with safeguards).
- [ ] All changes persist in SQLite.
- [ ] Changes appear in patient interface immediately.
- [ ] Sample phrases are seeded and editable.

---

## Phase 3 — Patient Communication Interface

**Goal:** Build the working patient experience with keyword navigation and text-to-speech.

### Requirements
1. Load enabled keywords and categories from the backend.
2. Display large, accessible keyword cards.
3. Category navigation tabs/filter.
4. Selected keyword displays associated message.
5. Speak, Stop, and Repeat buttons using Web Speech API `SpeechSynthesis`.
6. Speech speed and voice selection UI.
7. Larger-text preference toggle.
8. High-contrast preference toggle.
9. Speak-on-selection optional setting.
10. Urgent phrases always visible.
11. Accessible live-region announcements.
12. Graceful degradation when SpeechSynthesis is unavailable.
13. Loading, empty, error, and success states.

### Acceptance Criteria
- [ ] All enabled keywords appear as clickable cards.
- [ ] Category filtering works correctly.
- [ ] Selecting a keyword shows its message.
- [ ] Speak button reads message aloud.
- [ ] Stop and Repeat buttons work.
- [ ] Preferences persist (localStorage).
- [ ] Interface is keyboard-navigable.
- [ ] Graceful message when speech synthesis is unavailable.

---

## Phase 4 — AI-Assisted Communication

**Goal:** Add optional AI sentence formulation via a configurable backend provider.

### Requirements
1. Type & Speak interface for word fragments.
2. Backend calls a configurable OpenAI-compatible API.
3. Returns a small set of candidate sentences.
4. Handles provider errors, timeouts, missing config gracefully.
5. Never exposes credentials to the browser.
6. Never auto-speaks AI-generated messages.
7. User can edit suggestions before speaking.
8. Keyword-based communication always available as fallback.

### Acceptance Criteria
- [ ] Fragment input sends request to backend `/ai/suggest`.
- [ ] Backend returns structured suggestions.
- [ ] User must explicitly approve before speaking.
- [ ] User can edit the suggestion text.
- [ ] If AI provider is unconfigured, show honest status message.
- [ ] Keyword communication still works during AI unavailability.
- [ ] No credentials appear in browser JS or network responses.

---

## Phase 5 — Quality, Accessibility, Testing, and Deployment

**Goal:** Validate, harden, and document the complete MVP.

### Requirements
1. Comprehensive Pytest backend test suite.
2. Tests for: DB operations, auth, CRUD, AI error handling.
3. Keyboard accessibility verification.
4. Responsive layout verification.
5. Screen-reader label and live-region audit.
6. Error message and loading-state polish.
7. Security review (parameterized queries, no stack traces, no credential leaks).
8. Complete README with setup, execution, testing, deployment.
9. Representative screenshots.

### Acceptance Criteria
- [ ] All backend tests pass.
- [ ] No known security regressions.
- [ ] README commands work as documented.
- [ ] WCAG 2.1 AA checklist reviewed (manual audit note included).
- [ ] Application fully operable via keyboard alone.

---

## Design System Summary

| Token | Value |
|---|---|
| Primary color | `#2563EB` (calm blue) |
| Accent color | `#0EA5E9` (sky blue) |
| Urgent color | `#DC2626` (red) |
| Background | `#F8FAFC` |
| Surface | `#FFFFFF` |
| Text primary | `#0F172A` |
| Text secondary | `#475569` |
| Border | `#E2E8F0` |
| Radius (base) | `0.75rem` |
| Font | `'Space Mono', monospace` (Monotonic) |

---

## Security Limitations (Prototype Notice)

This is a local prototype, not a production medical application.

- PIN-based guardian access is suitable for single-device family use, not multi-user clinical deployment.
- SQLite is not appropriate for multi-server or high-concurrency production use.
- This application does not store, transmit, or process medical records.
- No warranty of fitness for any medical purpose is expressed or implied.
