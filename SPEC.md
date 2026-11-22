# Civic AI — System Specification

## 1. Overview & Problem Statement

Indian citizens face significant barriers when navigating digital public governance:
- **Complex Administrative Language:** Official government circulars, notifications, and gazette orders are drafted in dense legalistic prose that is difficult for everyday citizens to comprehend.
- **Fragmented Welfare Catalog:** Information regarding government welfare schemes is distributed across hundreds of central and state portals, with inconsistent eligibility criteria, application procedures, and verification links.
- **Language Exclusion:** While central notices are typically published in English or Hindi, millions of citizens require accurate policy explanations and application procedures in their native regional language.
- **Hallucinated Legal Information:** Generative AI tools often fabricate statutory provisions, deadlines, and welfare requirements when asked civic or legal questions.

Civic AI addresses these challenges through a unified digital platform providing:
1. An authoritative All-India scheme directory covering 4,859 verified welfare schemes across Central and 36 State/UT jurisdictions.
2. Fast full-text search powered by SQLite FTS5 (< 5ms response time).
3. A 100% deterministic rules engine for calculating citizen scheme eligibility without generative guesswork.
4. Plain-language notice and circular summarization down to Grade 6 reading levels with hard deadlines and action items.
5. Statutory legal rights exploration grounded in verified India Code Acts with mandatory section citations.
6. Full end-to-end localization across 12 official Indian languages.

---

## 2. Target Users

- **General Citizens:** Seeking to discover and verify entitlement to central and state welfare benefits for agriculture, healthcare, housing, pensions, education, and employment.
- **Grassroots Workers & Village Level Entrepreneurs (VLEs):** Assisting community members at Common Service Centres (CSCs) with eligibility checks and scheme applications.
- **Civic Advocates & Legal Volunteers:** Interpreting government notifications and advising citizens on tenancy, consumer rights, labor law, and RTI queries.

---

## 3. Implemented Features & Flows

### 3.1 Public Scheme Directory (`/eligibility`)
- **Authoritative Database:** Stores 4,859 verified public welfare schemes spanning the Central Government and all 36 States and Union Territories.
- **Fast Full-Text Search:** Implemented with SQLite FTS5 using the `unicode61` tokenizer to support queries in English and native regional scripts (Devanagari, Telugu, Tamil, Bengali, etc.).
- **Server-Side Pagination:** `GET /api/schemes` returns 24 schemes per page with total count, total pages, and active filter criteria, ensuring payload sizes remain under 200 KB and first-page loads finish in under 1 second.
- **Four-Tier Governance Classification:**
  - `central`: National schemes funded and administered centrally across all 28 States & 8 UTs.
  - `state`: Schemes administered and funded by a specific State or Union Territory government.
  - `integrated`: Centrally sponsored schemes implemented jointly with state governments, displaying state-specific application links where applicable.
  - `multi_state`: Regional schemes applicable to two or more designated states.
- **Portal & Application Links:** Every scheme includes verified direct application links (`direct_apply_url` and `official_url`) referencing official government domains (`*.gov.in`, `*.nic.in`).
- **Live Search Fallback:** When a search returns zero local results, users can trigger a live search against allow-listed official domains. Discovered schemes are structured, tagged with a "Live Web Verified" badge, and stored locally with multilingual translations.

### 3.2 Deterministic Eligibility Calculator (`/eligibility`)
- **Deterministic Python Evaluation:** Pure Python rules engine (`backend/app/services/eligibility/engine.py`) assessing citizen profiles without generative AI calls.
- **Profile Parameters:** Age, state of residence, monthly household income, caste/social category, gender, and occupation.
- **Tri-State Determination:**
  - `eligible`: Citizen meets all explicit statutory conditions.
  - `not_eligible`: Citizen fails one or more specific criteria, with the exact disqualifying condition reported.
  - `need_more_info`: Citizen profile is missing a mandatory parameter required by the scheme.
- **Strict State Isolation:** Schemes belonging to one state are never matched to residents of another state.

### 3.3 Notice & Circular Explainer (`/explain`)
- **Document Ingestion:** Accepts PDF uploads (up to 50MB) and direct text paste.
- **Text Extraction:** Utilizes PyMuPDF for native PDF text extraction, with multimodal AI vision OCR for scanned documents and low-resolution circular images.
- **Grade 6 Civic Breakdown:** Produces four structured sections:
  1. *What Changed:* Plain-language policy summary.
  2. *Who Is Affected:* Impacted citizen groups and income brackets.
  3. *Deadlines:* Key statutory cutoff dates and compliance timelines.
  4. *Required Actions:* Step-by-step citizen instructions.

### 3.4 Statutory Rights Explorer (`/rights`)
- **Mandatory India Code Citations:** Answers legal and citizen rights questions with explicit citations to official statutory Acts and section numbers.
- **Covered Domains:** Consumer disputes, tenancy and eviction, Right to Information (RTI), labor regulations, domestic protections, and arrest procedures.
- **Truthful Non-Verification:** If no official government statute or provision can be verified for a query, the system explicitly reports that no authoritative source was found rather than inventing an answer.

### 3.5 End-to-End Multilingual Experience
- **12 Official Indian Languages Supported:**
  - English (`en`), Hindi (`hi`), Telugu (`te`), Tamil (`ta`), Kannada (`kn`), Malayalam (`ml`), Marathi (`mr`), Bengali (`bn`), Gujarati (`gu`), Punjabi (`pa`), Odia (`or`), Urdu (`ur` with RTL layout).
- **Comprehensive Localization:** Translates all scheme metadata (name, ministry, summary, benefits, criteria, exclusions, documents, application steps), UI navigation, filter options, state names, document categories, and system status indicators.
- **Zero Raw English Fallbacks:** Validated by `scripts/check_translations.py` and automated test suites.

### 3.6 Solid-Tone Civic UI & Accessibility
- **Authoritative Palette:** Built with solid Civic Navy Blue fills (`#2563EB` / `#1D4ED8`), high-contrast typography, and dark/light mode toggles.
- **Vector Icons:** All UI elements use vector SVG icons via the universal `Icon` component.
- **Scroll Restoration:** Browser scroll position resets to the top on page reload and route navigation via `history.scrollRestoration = 'manual'`.

---

## 4. Data Sources & Allow-List Policy

All external facts and live retrieval operations strictly query allow-listed official domains defined in `config/allowed_domains.yaml`:
- `*.gov.in`
- `*.nic.in`
- `myscheme.gov.in`
- `data.gov.in`
- `indiacode.nic.in`
- `egazette.gov.in`
- `nalsa.gov.in`
- `services.india.gov.in`
- `dbtbharat.gov.in`

Any URL resolving outside this allow-list is rejected by the verification security middleware.

---

## 5. Technology Stack

### Backend
- **Framework:** FastAPI with Uvicorn (Python 3.10+)
- **Data Storage & Search:** SQLite FTS5 (`data/civic_ai.db`) and JSON storage (`data/schemes.json`)
- **Document Parsing:** PyMuPDF (`fitz`)
- **AI Integration:** Google GenAI SDK (wrapped in `backend/app/services/llm.py`)
- **Testing:** Pytest with Pytest-Asyncio and RESPX

### Frontend
- **Framework:** React 18 with Vite 5
- **Routing:** React Router v6
- **Styling:** Modular CSS variables supporting dark and light themes
- **Internationalization:** Custom lightweight React Context provider (`frontend/src/i18n/`)

---

## 6. Repository Layout

```
Civic_AI/
├── backend/
│   ├── app/
│   │   ├── api/                     # REST API route handlers
│   │   ├── config.py                # Environment and settings configuration
│   │   ├── main.py                  # FastAPI application entrypoint
│   │   └── services/                # Business logic and services
│   ├── requirements.txt             # Python backend dependencies
│   └── tests/                       # Pytest test suite (39 tests)
├── config/
│   ├── allowed_domains.yaml         # Government domain allow-list
│   └── languages.yaml               # Language definitions
├── data/
│   ├── civic_ai.db                  # SQLite database with FTS5 index
│   ├── schemes.json                 # Complete scheme database (4,859 schemes)
│   └── sync_progress.json           # Ingestion checkpoint state
├── frontend/
│   ├── src/                         # React application components and pages
│   ├── index.html                   # HTML entrypoint
│   ├── package.json                 # Frontend dependencies
│   └── vite.config.js               # Vite build configuration
├── scripts/
│   ├── check_translations.py        # Translation audit tool
│   └── sync_schemes.py              # Scheme ingestion pipeline
├── .env.example                     # Environment variables template
├── package.json                     # Root npm script runner
├── README.md                        # Project documentation
├── run_local.py                     # Concurrent server launcher
└── SPEC.md                          # System specification
```

---

## 7. Environment Variables

| Variable | Description |
|---|---|
| `LLM_API_KEY` | API key for the AI model (document summarization, OCR, and rights retrieval). Optional for offline operation. |
| `LLM_MODEL` | AI model name (defaults to `gemini-2.5-flash`). |
| `TAVILY_API_KEY` | Search API key for real-time government domain discovery. Optional for offline operation. |
| `VITE_API_URL` | Base URL of the backend API for the frontend client (defaults to `http://localhost:8000`). |

---

## 8. Verification & Quality Acceptance Criteria

1. **Test Suite:** All 39 backend tests in `backend/tests/` must pass with zero errors.
2. **Translation Completeness:** `scripts/check_translations.py` must verify 100% translation coverage across all 4,859 schemes and all 12 languages with zero missing keys.
3. **Frontend Compilation:** `npm run build` inside `frontend/` must compile with zero errors and zero warnings.
4. **Deterministic Evaluation:** Scheme eligibility tests must never invoke external generative AI models.
5. **Exact Data Representation:** UI counters must display exact numbers (4,859 schemes across 28 States & 8 UTs) without approximation signs.
