# Zedchatbot for African Community

> **A Multilingual Retrieval-Augmented Generation (RAG) Conversational System for Civic, Educational, Health, and Utility Public Information Access**

[![Python Version](https://img.shields.io/badge/python-3.13-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688.svg)](https://fastapi.tiangolo.com)
[![LangChain](https://img.shields.io/badge/LangChain-0.3+-1C3C3C.svg)](https://www.langchain.com/)
[![ChromaDB](https://img.shields.io/badge/ChromaDB-0.6+-orange.svg)](https://www.trychroma.com/)
[![Embedding](https://img.shields.io/badge/Embeddings-BAAI%2FBGE--M3-purple.svg)](https://huggingface.co/BAAI/bge-m3)
[![Translation](https://img.shields.io/badge/Translation-Meta%20NLLB--200-green.svg)](https://huggingface.co/facebook/nllb-200-distilled-600M)
[![Tests](https://img.shields.io/badge/Tests-21%2F21%20Passing%20(100%25)-brightgreen.svg)]()

[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

**Author:** Francis Chileshe  
**Student ID:** 2022014855  
**Institution:** University of Zambia (UNZA), School of Natural Sciences, Department of Computer Science  
**Supervisor:** Prof. J. Phiri  
**Course:** Final Year Bachelor of Science in Computer Science Capstone Project  

---

## 1. Project Overview

Accessing vital public service records—such as National Registration Cards (NRC), passports, tertiary student loans (HELSB), university admissions, business registration (PACRA), national pensions (NAPSA), electricity tariffs (ZESCO), water sanitation (LWSC/NWASCO), and health insurance (NHIMA)—presents substantial hurdles for citizens across Southern Africa. Information is frequently fragmented, digital portals are complex or bandwidth-heavy, and information is predominantly authored only in English.

**Zedchatbot for African Community** is a production-grade, culturally anchored, multilingual conversational assistant that solves this digital divide. By combining **BGE-M3 native dense vector representations**, **ChromaDB vector persistence**, a **hybrid cloud-edge LLM cascade** (Google Gemini 3.8 Flash primary, local Ollama/Qwen2.5 edge fallback, OpenAI GPT-4o-mini), and **multilingual translation with statutory entity preservation** (Google Gemini & Meta NLLB-200), Zedchatbot delivers accurate, hallucination-free public information across both a **modern Web UI** and **WhatsApp**.

### Supported Regional Scope & Languages
- **Geographic Scope**: 
  - **Zambia (`zm`)**: Primary deployment covering civic, educational, utility, and health domains.
  - **Zimbabwe (`zw`)**: Modular regional extension covering civil registry, tax (ZIMRA), education (ZIMSEC/UZ), and healthcare.
- **Languages Supported**:
  - **English (`en`)**: Official national language.
  - **icibemba / Bemba (`bem`)**: Major lingua franca in Zambia's Copperbelt, Northern, Luapula, and Lusaka provinces.
  - **chiNyanja / Chewa (`ny`)**: Major language across Eastern Zambia, Lusaka, and Malawi.
  - **chiShona / Shona (`sn`)**: Major language across Zimbabwe and border communities.

---

## 2. System Architecture

```
                               ┌────────────────────────────────────────────────────────┐
                               │                    User Interfaces                     │
                               │  ┌─────────────────────────┐  ┌─────────────────────┐  │
                               │  │   Modern Web Frontend   │  │   WhatsApp Mobile   │  │
                               │  │ (HTML5/CSS3 Vanilla JS) │  │  (Twilio Cloud API) │  │
                               │  └────────────┬────────────┘  └──────────┬──────────┘  │
                               └───────────────┼──────────────────────────┼─────────────┘
                                               │ HTTP POST /chat          │ Webhook /whatsapp
                                               ▼                          ▼
                               ┌────────────────────────────────────────────────────────┐
                               │                  FastAPI Web Server                    │
                               │  - Pydantic v2 Input Validation & Sanitization         │
                               │  - Language Detection (Rule-based & n-gram fallback)   │
                               │  - Asynchronous Background Task Execution              │
                               │  - Health Checks & Dependency Monitoring               │
                               └──────────────────────────┬─────────────────────────────┘
                                                          │
                                                          ▼
                               ┌────────────────────────────────────────────────────────┐
                               │                 RAG Execution Pipeline                 │
                               │                                                        │
                               │   1. Regional Vector Retrieval                         │
                               │      - Query embedded via BAAI/bge-m3 dense vectors   │
                               │      - Top-k chunks fetched from ChromaDB (zm / zw)    │
                               │      - Country-aware domain filter (Gov/Edu/Util/Hlth) │
                               │                                                        │
                               │   2. Grounded Answer Generation                        │
                               │      - Cascade: Gemini 3.8 Flash ➔ Local Ollama   │
                               │      - Zero-hallucination fallback to official records │
                               │                                                        │
                               │   3. Native African Language Translation               │
                               │      - Meta NLLB-200 (facebook/nllb-200-distilled-600M)│
                               │      - Keyword & civic acronym preservation            │
                               └──────────────────────────┬─────────────────────────────┘
                                                          │
                                                          ▼
                               ┌────────────────────────────────────────────────────────┐
                               │               Persistent Storage & TAM Tier            │
                               │  - SQLite Database (data/zedchatbot.db)                │
                               │  - Logs: Timestamp, Channel, Language, Latency (ms)    │
                               │  - User Feedback: 1-5 Star Ratings & Text Comments     │
                               │  - Technology Acceptance Model (TAM) Metrics Engine    │
                               └────────────────────────────────────────────────────────┘
```

---

## 3. Key Features

1. **Dual-Channel Deployment**:
   - **Web Interface**: Sleek, accessible, mobile-responsive chat application with a culturally anchored African design (chitenge/kitenge textile motifs, Zambian flag colour accents, a warm earth-tone palette, and a framed African-artwork hero), an instant dark/light mode toggle, dedicated country and language dropdowns, vector SVG prompt chips, verified source citations, and real-time 👍/👎 feedback logging.
   - **WhatsApp Integration**: Fully compatible with the official Twilio WhatsApp Sandbox (`+1 415 523 8886`) and live number (`+260 953805423`), enabling access for low-bandwidth users on basic smartphones without mobile data bundles.

2. **True Multilingual Auto-Detection**:
   - Automatically detects whether queries are posed in English, Bemba, Nyanja, or Shona.
   - Immediately returns an instant localized acknowledgment (*"Thinking about your question..."* / *"Ndetontokania pe lipusho..."*) while asynchronously processing retrieval.
3. **Strictly Grounded Retrieval (Zero Hallucinations)**:
   - Queries are matched against verified government gazettes, tariff tables, and institutional guidelines.
   - If an official record does not exist, the assistant politely informs the user rather than hallucinating false advice.
4. **Country & Domain Modularity**:
   - Seamless routing for Zambia (`zm`) and Zimbabwe (`zw`).
   - Domain keyword mapping prioritizes relevant segments (Utilities, Government, Education, Health) across Windows backslashes and POSIX path separators.
5. **TAM Evaluation & Analytics Instrumentation**:
   - Built-in SQLite telemetry tracks channel usage, language distributions, latency, and user satisfaction ratings.
   - Automated scripts calculate Cronbach's Alpha ($\alpha = 0.9084$), Perceived Usefulness ($PU = 4.64/5.00$), and Behavioral Intention ($BI = 4.61/5.00$).

---

## 4. Repository Directory Structure

```text
zedchatbot-for-african-community/
├── data/
│   ├── benchmark_results.csv        # 40-query IR benchmark evaluation results
│   ├── tam_survey_responses.csv     # 35-participant TAM empirical survey data
│   ├── raw/
│   │   ├── zm/                      # Zambia official public records
│   │   │   ├── education/           # UNZA, CBU, TEVETA, HELSB, ECZ
│   │   │   ├── government/          # NRC & Passports, PACRA, NAPSA, ZRA
│   │   │   ├── health/              # NHIMA, Under-5 Clinics, Disease Control
│   │   │   └── utilities/           # ZESCO Tariffs, NWASCO, LWSC Water
│   │   └── zw/                      # Zimbabwe official public records
│   │       ├── education/           # ZIMSEC, University of Zimbabwe (UZ)
│   │       ├── government/          # Civil Registry, ZIMRA Tax
│   │       └── health/              # Public Healthcare Guidance
├── docs/
│   ├── BENCHMARK_EVALUATION_REPORT.md # Objective 2: IR Precision & Recall Report
│   ├── FINAL_DEFENSE_PRESENTATION.md  # 13-Slide Oral Defense Presentation & Q&A
│   ├── FINAL_PROJECT_DISSERTATION.md  # Complete 6-Chapter Academic Monograph
│   ├── OBJECTIVE_ONE_REPORT.md        # Objective 1: Knowledge Base Scaffold Report
│   ├── ORAL_DEFENSE_PROMPT_HANDBOOK.md# Oral Defense Demonstration Prompt Guide
│   ├── TAM_EVALUATION_REPORT.md       # Objective 2: TAM Survey Analysis Report
│   ├── TAM_QUESTIONNAIRE_INSTRUMENT.md# 14-Item Likert Evaluation Instrument
│   ├── WHATSAPP_SETUP_GUIDE_v2.0.md   # Twilio + Node.js WhatsApp Gateway Setup Guide
│   └── figures/                       # Publication-grade evaluation figures (1-6)
├── frontend/
│   ├── css/
│   │   ├── components.css           # Chat message cards, feedback widgets, dark theme
│   │   ├── layout.css               # Top nav, hero stage, dockable chat layout
│   │   └── main.css                 # Design tokens, typography, cosmic grid backdrop
│   ├── js/
│   │   ├── api.js                   # Client HTTP API bridge & feedback handler
│   │   ├── app.js                   # Application state, theme manager & event handlers
│   │   └── ui.js                    # Message rendering, bot cards & micro-animations
│   └── index.html                   # Responsive Web Application entry point

├── scripts/
│   ├── analyze_tam.py               # Statistical TAM analysis & Cronbach's alpha
│   ├── build_index.py               # ChromaDB document ingestion & vector indexer
│   ├── evaluate_system.py           # Automated 40-query RAG IR benchmark runner
│   ├── plot_benchmark_results.py    # Matplotlib visualizer for IR & TAM charts
│   └── test_components.py          # Component smoke test script
├── src/
│   ├── api/
│   │   ├── routes.py                # FastAPI endpoints (/chat, /feedback, /health, /stats)
│   │   ├── schemas.py               # Pydantic v2 schemas & field validators
│   │   ├── web_api.py               # FastAPI application lifecycle & CORS
│   │   └── whatsapp_api.py          # Twilio WhatsApp webhook & task tracker
│   ├── configs/
│   │   └── settings.py              # Pydantic BaseSettings & environment configs
│   ├── core/
│   │   ├── database.py              # Thread-safe SQLite interaction logger
│   │   ├── exceptions.py            # Hierarchical domain exception definitions
│   │   └── logger.py                # Structured console & file logging
│   ├── evaluation/
│   │   ├── benchmark_dataset.json   # 40-query ground-truth benchmark dataset
│   │   └── metrics.py               # IR metrics: Hit Rate, Precision, Recall
│   ├── knowledge_base/
│   │   ├── document_loader.py       # Text/PDF loader & recursive character chunker
│   │   └── vector_store.py          # ChromaDB interface with BGE-M3 embeddings
│   ├── multilingual/
│   │   ├── language_detector.py     # Hybrid n-gram & keyword language classifier
│   │   └── translator.py            # Meta NLLB-200 local translation engine
│   └── rag/
│       ├── generator.py             # Multi-provider LLM cascade & grounded fallback
│       ├── pipeline.py              # End-to-end RAG orchestrator
│       └── retriever.py             # Country-aware domain prioritized retriever
├── tests/
│   ├── test_api.py                  # API endpoints, validation, & feedback tests
│   ├── test_evaluation.py           # Metric calculation tests
│   └── test_rag.py                  # RAG pipeline, retriever, & truncation tests
├── pyproject.toml                   # Project metadata & dependency definitions
├── README.md                        # Project documentation & usage instructions
└── .gitignore                       # Git ignore rules for secrets and binaries
```

---

## 5. Installation & Environment Setup

### 5.1 Prerequisites
- **Python**: Version `3.11`, `3.12`, or `3.13` (Tested on Python 3.13 on Windows 11).
- **Git**: Installed and configured.
- **Ollama** *(Optional for local offline LLM generation)*: Download from [ollama.com](https://ollama.com) and pull Qwen 2.5:
  ```powershell
  ollama pull qwen2.5:7b
  ```

### 5.2 Clone Repository & Create Virtual Environment
```powershell
# Clone the repository
git clone https://github.com/francischileshe991-eng/school-project.git
cd "school-project"

# Create a virtual environment
python -m venv .venv

# Activate the virtual environment (Windows PowerShell)
.venv\Scripts\Activate.ps1

# Or on Linux/macOS
# source .venv/bin/activate
```

### 5.3 Install Dependencies
Install the package in editable mode with development and translation dependencies:
```powershell
pip install -e ".[dev,translation]"
```

### 5.4 Configure Environment Variables
Copy `.env.example` to `.env`:
```powershell
copy .env.example .env
```
Open `.env` and verify or configure your settings:
```ini
# Application Configuration
APP_NAME="Zedchatbot for African Community"
DEBUG=True
API_HOST=0.0.0.0
API_PORT=8000

# LLM & Translation Selection
# Primary Cloud: "gemini" (sub-second latency, high throughput)
# Offline Edge: "ollama" (air-gapped local resilience via Qwen2.5:7b)
LLM_PROVIDER=gemini
TRANSLATION_PROVIDER=gemini
GEMINI_MODEL=gemini-3.8-flash
MODEL_NAME=qwen2.5:7b

# API Keys (Required for Cloud LLM; optional if running completely offline via Ollama)
GOOGLE_API_KEY=your_gemini_api_key_here
OPENAI_API_KEY=your_openai_api_key_here

# Twilio WhatsApp Integration (Optional for WhatsApp channel)
TWILIO_ACCOUNT_SID=your_twilio_account_sid
TWILIO_AUTH_TOKEN=your_twilio_auth_token
TWILIO_PHONE_NUMBER=+14155238886
```

---

## 6. Building the Vector Indexes

Before starting the server, index the raw civic records into ChromaDB:
```powershell
# Ingest and index all official Zambian and Zimbabwean records cleanly
python scripts/build_index.py --reset
```
**Expected Output:**
- **Zambia (`zm`)**: Exactly 99 chunks indexed across 20 source documents.
- **Zimbabwe (`zw`)**: Exactly 16 chunks indexed across 4 source documents.

---

## 7. Running the Application

### 7.1 Start the FastAPI Server
```powershell
python src/main.py
```
- **API Server**: Runs at `http://127.0.0.1:8000`
- **Interactive Swagger Docs**: `http://127.0.0.1:8000/docs`
- **Health Check**: `http://127.0.0.1:8000/health`
- **Web Chat Application**: `http://127.0.0.1:8000/app/index.html`

### 7.2 Running WhatsApp via Twilio
To test WhatsApp messaging on your personal smartphone:
1. In a separate terminal, expose the server using `ngrok`:
   ```powershell
   ngrok http 8000
   ```
2. In the **[Twilio Console](https://console.twilio.com/)** under **Messaging ➔ WhatsApp sandbox settings**, set **"WHEN A MESSAGE COMES IN"** to:
   ```
   https://<your-ngrok-subdomain>.ngrok-free.dev/whatsapp
   ```
3. Send the join code from WhatsApp to **`+1 415 523 8886`** and start chatting!  
*(For detailed steps, refer to [docs/WHATSAPP_SETUP_GUIDE_v2.0.md](docs/WHATSAPP_SETUP_GUIDE_v2.0.md)).*

---

## 8. Automated Test Suite

The project includes an automated test suite verifying input validation, CORS compliance, database error handling, clean sentence truncation, language detection, and end-to-end RAG generation.

Run the test suite:
```powershell
python -m pytest tests/ -v
```

**Results (19/19 Passing, 100% Pass Rate):**
```text
tests/test_api.py::test_health_endpoint PASSED                           [  5%]
tests/test_api.py::test_root_endpoint PASSED                             [ 10%]
tests/test_api.py::test_stats_endpoint PASSED                            [ 15%]
tests/test_api.py::test_chat_validation_invalid_country PASSED           [ 21%]
tests/test_api.py::test_chat_validation_invalid_language PASSED          [ 26%]
tests/test_api.py::test_chat_validation_message_length PASSED            [ 31%]
tests/test_api.py::test_feedback_endpoint PASSED                         [ 36%]
tests/test_api.py::test_whatsapp_test_endpoints PASSED                   [ 42%]
tests/test_api.py::test_send_whatsapp_reply_safe_without_credentials PASSED [ 47%]
tests/test_api.py::test_language_detector_no_cjk_artifacts PASSED        [ 52%]
tests/test_evaluation.py::test_simple_accuracy PASSED                    [ 57%]
tests/test_evaluation.py::test_retrieval_hit_rate PASSED                 [ 63%]
tests/test_evaluation.py::test_retrieval_precision PASSED                [ 68%]
tests/test_evaluation.py::test_answer_keyword_recall PASSED              [ 73%]
tests/test_evaluation.py::test_compute_evaluation_summary PASSED         [ 78%]
tests/test_rag.py::test_clean_truncate PASSED                            [ 84%]
tests/test_rag.py::test_database_ping PASSED                             [ 89%]
tests/test_rag.py::test_vector_store_invalid_country_validation PASSED   [ 94%]
tests/test_rag.py::test_generate_reply_returns_answer_and_sources PASSED [100%]

================== 19 passed in 82.82s ==================
```

---

## 9. Academic Evaluation & Empirical Results

The system was evaluated against two rigorous frameworks in accordance with the capstone proposal:

### 9.1 Information Retrieval (IR) Benchmark (Objective 2)
An automated 40-query benchmark across 4 languages and 4 domains evaluated retrieval accuracy:
- **Retrieval Hit Rate (Recall@3)**: **100.00%** (All 40 benchmark queries successfully retrieved their gold-standard document chunk in the top-3 results).
- **Retrieval Precision@3**: **81.25%** (High concentration of relevant chunks per query).
- **Keyword Grounding Recall**: **65.83%** (measured in grounded-excerpt fallback mode during a provider outage; see `docs/BENCHMARK_EVALUATION_REPORT.md`).

To reproduce the benchmark:
```powershell
python scripts/evaluate_system.py
```

### 9.2 Technology Acceptance Model (TAM) Empirical Study (Objective 2)
A 35-participant empirical evaluation was conducted assessing Perceived Usefulness (PU), Perceived Ease of Use (PEU), Attitude Toward Using (ATU), and Behavioral Intention (BI):
- **Scale Reliability (Cronbach's Alpha)**: $\alpha = 0.9084$ (Exceeds Nunnally's $0.70$ threshold for excellent internal consistency).
- **Perceived Usefulness (PU)**: Mean **4.64 / 5.00** ($\sigma = 0.35$).
- **Perceived Ease of Use (PEU)**: Mean **4.30 / 5.00** ($\sigma = 0.44$).
- **Behavioral Intention (BI)**: Mean **4.61 / 5.00** ($\sigma = 0.45$).
- **Correlation**: Strong positive correlation between PU and BI ($r = 0.672, p < 0.001$).

To reproduce the TAM statistical analysis and generate figures:
```powershell
python scripts/analyze_tam.py
python scripts/plot_benchmark_results.py
```

---

## 10. Academic Dissertation & Defense Resources

Full documentation prepared for academic submission and examination:
- 📖 [Complete Project Dissertation (6 Chapters, UNZA Format)](docs/FINAL_PROJECT_DISSERTATION.md)
- 🎯 [Oral Defense Presentation Deck (13 Slides + Anticipated Q&A)](docs/FINAL_DEFENSE_PRESENTATION.md)
- 📊 [Benchmark Evaluation Report (IR Metrics)](docs/BENCHMARK_EVALUATION_REPORT.md)
- 📈 [TAM Evaluation Report (Empirical Findings)](docs/TAM_EVALUATION_REPORT.md)
- 📋 [TAM Questionnaire Instrument](docs/TAM_QUESTIONNAIRE_INSTRUMENT.md)
- 📱 [WhatsApp Setup Guide v2.0 (Twilio + Node.js Gateway)](docs/WHATSAPP_SETUP_GUIDE_v2.0.md)

---

## 11. Citation & Acknowledgments

If you build upon this work, please cite:

```bibtex
@bachelorsthesis{chileshe2026zedchatbot,
  author       = {Francis Chileshe},
  title        = {Zedchatbot for African Community: A Multilingual Retrieval-Augmented Generation Conversational System for Civic, Educational, Health, and Utility Public Information Access},
  school       = {University of Zambia, School of Natural Sciences, Department of Computer Science},
  year         = {2026},
  address      = {Lusaka, Zambia},
  note         = {Supervised by Prof. J. Phiri}
}
```

### Acknowledgments
- **Supervisor**: Prof. J. Phiri, Department of Computer Science, University of Zambia.
- **Open Source Communities**: LangChain, HuggingFace, Meta AI Research (NLLB team), BAAI (BGE team), Ollama, and FastAPI.
