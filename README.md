# Civic AI - Policy & Rights Explainer for Indian Citizens 🏛️

> **Multilingual Digital Public Governance & Citizen Intelligence Platform**  
> Indexes **4,859 verified Central & State/UT welfare schemes** across all 28 Indian States & 8 Union Territories, powered by SQLite FTS5 search (< 5ms), 100% deterministic eligibility evaluation, end-to-end multilingual localization across **12 official Indian languages**, and mandatory India Code statutory citations.

---

## ⚡ 3-Step Local Quickstart

Get the entire application up and running locally in under 2 minutes:

### Step 1: Install Dependencies
```bash
# Backend requirements (Python 3.10+)
pip install -r backend/requirements.txt

# Frontend requirements (Node.js 18+)
cd frontend && npm install && cd ..
```

### Step 2: Configure Environment
```bash
# Copy the minimal template to .env
cp .env.example .env
```
*(Both `LLM_API_KEY` and `TAVILY_API_KEY` are optional. If left unconfigured, Civic AI automatically uses built-in local offline fallback datasets and deterministic rules so all modules function fully offline without crashing).*

### Step 3: Run the Application
Launch both backend and frontend concurrently with a single command:
```bash
python run_local.py
```
*(Or run individual services: `python run_local.py --backend` or `python run_local.py --frontend`)*

---

## 🌐 Access Points
- **Frontend Web Portal:** [http://localhost:5173](http://localhost:5173)
- **Scheme Directory & Eligibility Checker:** [http://localhost:5173/eligibility](http://localhost:5173/eligibility)
- **Notice Explainer:** [http://localhost:5173/explain](http://localhost:5173/explain)
- **Statutory Rights Explorer:** [http://localhost:5173/rights](http://localhost:5173/rights)
- **Backend REST API:** [http://localhost:8000](http://localhost:8000)
- **Interactive Swagger Docs:** [http://localhost:8000/docs](http://localhost:8000/docs)
- **Health Check Probe:** [http://localhost:8000/health](http://localhost:8000/health)
- **Live Statistics API:** [http://localhost:8000/api/stats](http://localhost:8000/api/stats)
- **Supported Languages API:** [http://localhost:8000/api/languages](http://localhost:8000/api/languages)

---

## 🌟 Core Modules & Architecture

### 1. 🔍 Complete All-India Public Scheme Directory & SQLite FTS5 Engine (`/eligibility`)
- **Authoritative Public Ingestion (4,859 Official Schemes):**
  - High-performance ingestion pipeline (`scripts/sync_schemes.py`) that syncs the complete active catalog from official government APIs (`myScheme.gov.in`, `data.gov.in`).
  - Indexed into SQLite with **FTS5 full-text search** (`data/civic_ai.db`) and persistent `data/schemes.json` enabling **< 5ms search queries** across all 4,859 schemes using unicode61 tokenization for both English and regional scripts (Devanagari, Telugu, Tamil, Bengali, etc.).
  - Every scheme traces directly to verified official source portals (`*.gov.in`, `*.nic.in`).
- **Exact Live Count Display:**
  - Dynamic count banner reporting exact live figures without "+" signs: **4,859 Schemes Indexed across 28 States & 8 Union Territories**.
  - Server-side pagination (`page=1&page_size=24`) with fast payload responses under 200 KB and sub-second load times.
- **Complete Governance Classification & Direct Apply Links:**
  - Four distinct governance classifications: `central`, `state`, `integrated`, and `multi_state`.
  - Jurisdiction scope clearly identified: All-India, regional multi-state, or specific State/UT.
  - Direct clickable `Apply Now` button for single-portal schemes, and **individual per-state clickable portal links** for integrated schemes.
- **Live Web + AI Synthesis Fallback:**
  - When searching for a brand-new or unindexed scheme with zero local matches, citizens can trigger **AI Live Search**.
  - Fetches live guidelines from allow-listed government domains (`*.gov.in`, `*.nic.in`), extracts structured policy breakdowns, flags results with a **"Live Web Verified"** badge, and caches them locally with full regional translations.

### 2. 🌐 Full Multilingual Application (12 Official Indian Languages)
- **Global Language Switcher in Navbar:**
  - Seamlessly switch between **12 official Indian languages**:
    1. **English** (`en`)
    2. **Hindi (हिन्दी)** (`hi`)
    3. **Telugu (తెలుగు)** (`te`)
    4. **Tamil (தமிழ்)** (`ta`)
    5. **Kannada (ಕನ್ನಡ)** (`kn`)
    6. **Malayalam (മലയാളം)** (`ml`)
    7. **Marathi (मराठी)** (`mr`)
    8. **Bengali (বাংলা)** (`bn`)
    9. **Gujarati (ગુજરાતી)** (`gu`)
    10. **Punjabi (ਪੰਜਾਬੀ)** (`pa`)
    11. **Odia (ଓଡ଼ିଆ)** (`or`)
    12. **Urdu (اردو)** (`ur`) (with automatic RTL layout support)
  - Selected language is persisted in `localStorage` (`civic_ai_lang`) and synchronized across all pages, navigation items, filter pills, form inputs, buttons, and section headers.
- **100% Multilingual Translation Coverage:**
  - Every single scheme record in `data/schemes.json` is pre-translated across all 11 regional languages for: scheme name, summary, ministry/department, benefits, eligibility criteria, exclusions, required documents, and application steps.
  - Verification script `scripts/check_translations.py` audits translation completeness and enforces 100% coverage.
  - All UI strings, options, state names, document types, and badges are managed through `t()` with keys verified present across all 12 languages.
- **Solid-Tone Civic UI Design System:**
  - Solid single-tone Civic Navy Blue fills (`#2563EB` primary, `#1D4ED8` hover in dark mode; `#1D4ED8` primary, `#1E40AF` hover in light mode) paired with clean 1px hairline borders, high-contrast text, and neutral glass surfaces.
  - All UI icons use accessible SVG vector icons via the universal `Icon` component.
  - Page scroll opens at top on reload and navigation (`history.scrollRestoration = 'manual'`).

### 3. 🎯 Deterministic Scheme Eligibility Calculator (`/eligibility`)
- **100% Deterministic Python Rules Engine:**
  - Pure Python rule evaluation (`backend/app/services/eligibility/engine.py`) using explicit thresholds: age, state/UT, monthly household income, caste/social category, gender, and occupation.
  - **Zero LLM guessing or hallucination** in eligibility decisions.
- **Tri-State Decision Outcomes:**
  - **Eligible (Green):** User satisfies all statutory criteria.
  - **Not Eligible (Red):** Displays exact failing condition (e.g. income limit exceeded, state mismatch).
  - **Need More Info (Amber):** Identifies missing profile data required for determination.
- **State Isolation Enforcement:**
  - State-specific schemes strictly evaluate against the resident's state. Maharashtra schemes never match a Karnataka resident.

### 4. 📄 Document & Notice Explainer (`/explain`)
- **Multimodal Document Processing:**
  - Ingests official circulars, notifications, gazettes, and tax notices via PDF file upload or direct text paste.
  - Extracts text via PyMuPDF with vision-based multimodal fallback for scanned documents and low-resolution images.
- **Grade 6 Plain-Language Civic Summary:**
  - Transforms bureaucratic legal language into clear, grade-6 level explanations.
  - Highlights: What Changed, Who is Affected, Hard Deadlines, and Step-by-Step Required Actions.

### 5. ⚖️ Statutory Rights & Citizen Law Explorer (`/rights`)
- **Mandatory India Code Statutory Grounding:**
  - Answers citizen legal queries (tenancy rights, consumer protection, RTI applications, labor laws, arrest procedures).
  - Every answer must cite official Acts and sections from India Code (e.g., *Consumer Protection Act, 2019, Section 2(7)*).
  - If no official source can be located, the system explicitly reports that no official source could be verified rather than fabricating legal text.

---

## 📁 Repository Structure

```
Civic_AI/
├── backend/
│   ├── app/
│   │   ├── api/                     # REST API routers
│   │   │   ├── eligibility.py       # Scheme directory, pagination & calculator endpoints
│   │   │   ├── explain.py           # Document notice explainer endpoint
│   │   │   ├── languages.py         # Supported languages metadata endpoint
│   │   │   ├── rights.py            # Statutory rights query endpoint
│   │   │   ├── states.py            # 28 States & 8 UTs list endpoint
│   │   │   ├── stats.py             # Live catalog statistics endpoint
│   │   │   └── verify.py            # Domain whitelisting & freshness verification
│   │   ├── config.py                # Pydantic Settings with LLM_API_KEY & LLM_MODEL
│   │   ├── main.py                  # FastAPI application entrypoint & middleware
│   │   └── services/                # Core domain business logic
│   │       ├── eligibility/         # Deterministic rules engine & SQLite FTS5 search
│   │       ├── explain/             # PDF text extraction & plain-language summarizer
│   │       ├── llm.py               # Vendor-neutral LLM service wrapper
│   │       ├── rights/              # Statutory grounding & India Code retrieval
│   │       └── verify/              # Official domain allow-list validator
│   ├── requirements.txt             # Lean backend Python dependencies
│   └── tests/                       # Complete pytest test suite (39 passing tests)
├── config/
│   ├── allowed_domains.yaml         # Official government domain whitelist (*.gov.in, *.nic.in)
│   └── languages.yaml               # 12 official supported Indian languages
├── data/
│   ├── civic_ai.db                  # SQLite FTS5 search index (unicode61 tokenizer)
│   ├── schemes.json                 # Complete catalog of 4,859 schemes with full translations
│   └── sync_progress.json           # Ingestion pipeline resume state
├── frontend/
│   ├── src/
│   │   ├── components/              # Reusable UI components (Icon, SourceBadge, UploadCard, etc.)
│   │   ├── i18n/                    # 12-language translation dictionary (translations.js)
│   │   ├── pages/                   # Route views (HomePage, EligibilityPage, ExplainPage, RightsPage)
│   │   ├── services/                # Client-side scheme translation & caching service
│   │   └── utils/                   # Lexicon & ministry translators
│   ├── index.html                   # HTML entrypoint with vector civic landmark favicon
│   ├── package.json                 # Frontend dependencies (React 18, Vite 5)
│   └── vite.config.js               # Vite build configuration
├── scripts/
│   ├── check_translations.py        # Audit script verifying 100% translation coverage
│   └── sync_schemes.py              # Single ingestion pipeline for all-India scheme sync
├── .env.example                     # Environment configuration template
├── package.json                     # Root convenience npm scripts
├── README.md                        # Project documentation and user guide
├── run_local.py                     # Single-command concurrent launcher
└── SPEC.md                          # Baseline system specification
```

---

## 🛠️ Data Pipeline & Translation Audit

### Ingestion Pipeline
To synchronize the scheme catalog from official government sources:
```bash
python scripts/sync_schemes.py
```
This updates `data/schemes.json` and rebuilds the SQLite FTS5 index in `data/civic_ai.db`.

### Translation Verification
To audit multilingual translation coverage across all 4,859 schemes and all 12 languages:
```bash
python scripts/check_translations.py
```

---

## 🧪 Running Tests

Civic AI includes a comprehensive test suite covering all modules:
```bash
# Run all backend tests
pytest backend/tests -v
```

---

## 🔑 Environment Variables

| Variable | Description | Default | Required |
|---|---|---|---|
| `LLM_API_KEY` | API Key for the AI model (summarization, vision OCR, rights retrieval) | None | No (Local offline fallbacks used if unset) |
| `LLM_MODEL` | AI model name | None | No |
| `TAVILY_API_KEY` | Search API Key for real-time live portal lookups | Not Specific | No (Offline catalog used if unset) |
| `VITE_API_URL` | Base URL of the backend API for the frontend client | `http://localhost:8000` | No |

---

## ⚖️ Legal Disclaimer

Civic AI is an educational digital public infrastructure project providing public scheme intelligence and statutory rights explanations based on official publications. It does not provide formal legal representation or substitute for licensed legal counsel. For free government legal assistance, contact the National Legal Services Authority (NALSA) toll-free helpline at **15100**.
