# Objective One Implementation Report

## "Design and implement a modular Retrieval-Augmented Generation (RAG) based conversational AI system..."

---

## 1. System Overview

**Zedchatbot** is a multilingual RAG (Retrieval-Augmented Generation) chatbot designed to serve African communities. The system provides citizens with access to trusted information about government services, education, utilities, health, and general local information.

### Technology Stack

| Component | Technology | Purpose |
|-----------|------------|---------|
| **Backend Framework** | FastAPI + Uvicorn | REST API server |
| **RAG Orchestration** | LangChain | Pipeline management |
| **Vector Database** | ChromaDB | Semantic document storage |
| **Embeddings** | BGE-M3 (HuggingFace) | Native multilingual embeddings |
| **LLM (Local)** | Qwen2.5:7b via Ollama | Response generation |
| **Translation** | NLLB-200 (Meta) | Language translation |
| **Language Detection** | langdetect + custom keywords | Detect Bemba, Nyanja, Shona |
| **Web Interface** | Vanilla HTML/CSS/JS | User interaction |
| **Messaging** | Twilio WhatsApp | Alternative access channel |

---

## 2. Modular Architecture

The system follows a **modular architecture** with clearly separated concerns:

```
src/
├── api/                      # API Layer
│   ├── routes.py            # Chat & health endpoints
│   ├── schemas.py           # Request/response models (Pydantic)
│   ├── web_api.py           # FastAPI app configuration
│   └── whatsapp_api.py      # Twilio webhook integration
│
├── rag/                      # RAG Pipeline
│   ├── pipeline.py          # Orchestrates entire RAG flow
│   ├── retriever.py         # Vector search & context retrieval
│   └── generator.py         # LLM response generation
│
├── knowledge_base/          # Document Processing
│   ├── document_loader.py   # PDF/TXT loading
│   ├── indexer.py          # Document chunking & indexing
│   └── vector_store.py     # ChromaDB management
│
├── multilingual/            # Language Support
│   ├── language_detector.py # Detect user language
│   └── translator.py        # NLLB translation service
│
├── core/                    # Utilities
│   ├── logger.py           # Logging system
│   └── exceptions.py       # Custom exceptions
│
└── configs/
    └── settings.py         # Configuration management
```

### Key Design Principles

1. **Separation of Concerns**: Each module handles one specific responsibility
2. **Country-Specific Isolation**: Each country has its own vector database (`vector_store/zm/`, `vector_store/zw/`)
3. **Lazy Initialization**: Resources (models, pipelines) are loaded on-demand
4. **Configuration via Environment**: All settings managed through `.env` file

---

## 3. RAG Pipeline Implementation

### 3.1 Document Retrieval (`src/rag/retriever.py`)

The retriever component handles semantic search across the knowledge base:

```python
class ZedRetriever:
    def get_relevant_context(self, query: str, country_code: str, top_k: int = 3):
        # Searches country-specific ChromaDB vector store
        # Returns top-k most relevant document chunks
```

**Key Features:**
- Country-specific search (Zambia, Zimbabwe isolated)
- Configurable result count (`top_k`)
- Distance-based relevance scoring

### 3.2 Response Generation (`src/rag/generator.py`)

The generator uses local Ollama (Qwen2.5) for response creation:

```python
class ZedGenerator:
    def generate(self, query: str, context: str, country: str, language: str) -> str:
        # Uses retrieved context + query to generate answer
        # Supports native multilingual output
```

**Key Features:**
- Local LLM (no API costs, privacy-preserving)
- Language-aware response generation
- Graceful fallback if Ollama unavailable

### 3.3 End-to-End Pipeline (`src/rag/pipeline.py`)

The main pipeline orchestrates the entire RAG flow:

```python
def generate_reply(message: str, country: str, language: str = None):
    1. Detect user language (English/Bemba/Nyanja/Shona)
    2. Search vector store with native multilingual query
    3. Retrieve relevant context documents
    4. Generate response using Qwen2.5
    5. Fallback translation if needed
    6. Return answer with source citations
```

---

## 4. Curated Knowledge Base

### 4.1 Document Categories

The system supports knowledge bases organized by country and domain:

```
data/raw/
├── zm/                       # Zambia Knowledge Base
│   ├── government/          # NRC, Passport, ZRA documents
│   ├── education/            # ECZ, University admissions
│   ├── utilities/            # ZESCO, Water services
│   ├── health/               # NHIMA, Disease guidance
│   └── general/              # Local information
│
└── zw/                       # Zimbabwe Knowledge Base
    └── ...                   # Similar structure
```

### 4.2 Supported Domains

| Domain | Examples | Status |
|--------|----------|--------|
| **Government Services** | NRC, Passport, ZRA (taxes) | Implemented |
| **Education** | ECZ (examinations), UNZA admissions | Implemented |
| **Utilities** | ZESCO (electricity), Water bills | Implemented |
| **Health** | NHIMA (insurance), Disease guidance | Implemented |
| **Elections** | ECZ information | Implemented |
| **General Local Info** | Community resources | Implemented |

### 4.3 Document Processing Pipeline

```
data/raw/*.pdf, *.txt
         ↓
    ZedDocumentLoader
         ↓
    Text Cleaning & Chunking
         ↓
    BGE-M3 Embedding Generation
         ↓
    ChromaDB Vector Storage
         ↓
    Semantic Search Ready
```

---

## 5. Multilingual Support

### 5.1 Supported Languages

| Code | Language | Detection Method |
|------|----------|------------------|
| `en` | English | langdetect |
| `bem` | Bemba | Keyword + langdetect hybrid |
| `ny` | Nyanja (Chichewa) | Keyword + langdetect hybrid |
| `sn` | Shona | Keyword + langdetect hybrid |

### 5.2 Language Detection (`src/multilingual/language_detector.py`)

Custom detection with keyword fallback for African languages:

- **Signature words** for each language (Bemba: "mwapoleni", Nyanja: "muli bwanji", Shona: "mhoro")
- **Phrase matching** for common expressions
- **Confidence scoring** with keyword override capability

### 5.3 Translation Service (`src/multilingual/translator.py`)

- **Model**: Meta NLLB-200 distilled 600M
- **Features**:
  - Keyword protection (NHIMA, ZRA, UNZA, etc.)
  - Greeting caching for fast responses
  - Lazy model loading

### 5.4 Native Multilingual RAG

The system supports **native multilingual interaction**:

1. User queries in Bemba/Nyanja/Shona
2. BGE-M3 embeddings handle cross-lingual search natively
3. Qwen2.5 generates responses in detected language
4. Translation fallback only when LLM output doesn't match expected language

---

## 6. Interface Support

### 6.1 Web Interface

**Location**: `frontend/index.html`

Features:
- Country selection (Zambia/Zimbabwe)
- Language selection (English/Bemba/Nyanja/Shona)
- Real-time chat interface
- Source citations display
- Mobile-responsive design

### 6.2 WhatsApp Integration

**Endpoint**: `POST /whatsapp`

- Twilio webhook integration
- WhatsApp sandbox ready
- Same RAG pipeline for responses
- Automatic source attribution

### 6.3 REST API

**Endpoints**:

| Method | Path | Purpose |
|--------|------|---------|
| `GET` | `/health` | System health check |
| `GET` | `/` | API landing page |
| `POST` | `/chat` | Main chat endpoint |
| `POST` | `/whatsapp` | WhatsApp webhook |

---

## 7. Multi-Country Extensibility

### 7.1 Adding New Countries

The architecture supports **easy addition of new countries**:

1. Create country directory: `data/raw/{country_code}/`
2. Add documents organized by domain
3. Run ingestion pipeline to populate vector store
4. Add country code to `settings.py` → `SUPPORTED_COUNTRIES`
5. Update frontend dropdown

**No code changes required** for the RAG pipeline itself.

### 7.2 Country Isolation

Each country maintains an **independent vector store**:
- `vector_store/zm/` - Zambia
- `vector_store/zw/` - Zimbabwe

This ensures:
- Data isolation between countries
- Independent scaling of knowledge bases
- Country-specific configuration flexibility

---

## 8. Configuration Management

All settings centralized in `src/configs/settings.py`:

```python
# Core Settings
MODEL_NAME = "qwen2.5:7b"
EMBEDDING_MODEL = "BAAI/bge-m3"
VECTOR_STORE_PATH = "./vector_store"

# Regional Settings
DEFAULT_COUNTRY = "zm"
DEFAULT_LANGUAGE = "en"
SUPPORTED_COUNTRIES = ["zm", "zw"]
SUPPORTED_LANGUAGES = ["en", "bem", "ny", "sn"]
```

Configuration loaded from `.env` file with Pydantic validation.

---

## 9. Source Code Summary

### File Inventory

| Component | Files |
|-----------|-------|
| **API Layer** | `routes.py`, `schemas.py`, `web_api.py`, `whatsapp_api.py` |
| **RAG Pipeline** | `pipeline.py`, `retriever.py`, `generator.py` |
| **Knowledge Base** | `document_loader.py`, `indexer.py`, `vector_store.py` |
| **Multilingual** | `language_detector.py`, `translator.py` |
| **Core** | `logger.py`, `exceptions.py`, `settings.py` |
| **Frontend** | `index.html`, `css/*.css`, `js/app.js` |
| **Documentation** | `docs/*.md` |

---

## 10. Verification Checklist

| Objective Requirement | Implementation Status | Location |
|-----------------------|----------------------|----------|
| Modular RAG system | ✅ Implemented | `src/rag/pipeline.py` |
| Zambian knowledge base | ✅ Implemented | `data/raw/zm/` |
| Government services (NRC, passport, ZRA) | ✅ Supported | Document categories |
| Education (ECZ, university) | ✅ Supported | Document categories |
| Utilities (ZESCO, water) | ✅ Supported | Document categories |
| Health (NHIMA, disease) | ✅ Supported | Document categories |
| Web interface | ✅ Implemented | `frontend/` |
| WhatsApp interface | ✅ Implemented | `src/api/whatsapp_api.py` |
| English support | ✅ Implemented | Default language |
| Bemba support | ✅ Implemented | Language detector + translator |
| Nyanja support | ✅ Implemented | Language detector + translator |
| Modular architecture | ✅ Implemented | Country-specific vector stores |
| Easy country addition | ✅ Supported | Country isolation design |

---

## 11. Key Technical Highlights

1. **No External API Dependencies**: Uses local Ollama for LLM, reducing costs and ensuring privacy
2. **Native Multilingual**: BGE-M3 embeddings support cross-lingual retrieval without translation
3. **Production-Ready**: FastAPI with proper error handling, logging, and validation
4. **Scalable**: Country-specific databases can be updated independently
5. **Maintainable**: Clean separation of concerns with typed interfaces

---

*Document generated for Objective One progress report submission.*
*Zedchatbot for African Community*