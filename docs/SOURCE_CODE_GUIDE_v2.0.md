# Source Code & System Architecture Guide v2.0
**Project:** ZedChatBot for African Community  
**Researcher:** Francis Chileshe (Student ID: 2022014855)  
**Institution:** University of Zambia (UNZA) — Department of Computer Science  
**Supervisor:** Prof. J. Phiri  
**Version:** 2.0 (Complete System Implementation Reference)

---

## 1. System Overview & Architecture

ZedChatBot is a production-grade, culturally anchored, multilingual conversational assistant designed to bridge the digital divide for civic, educational, health, and utility public information access in Southern Africa (specifically Zambia and Zimbabwe).

```
 ┌─────────────────────────────────────────────────────────────────────────────┐
 │                             USER INTERFACES                                 │
 │  ┌─────────────────────────────────────┐  ┌──────────────────────────────┐  │
 │  │   Modern Web Frontend (HTML5/CSS3)  │  │   WhatsApp Mobile Messenger  │  │
 │  │   Glassmorphic UI, Sound, Feedback  │  │   (Real Number: +260953805423)│  │
 │  └──────────────────┬──────────────────┘  └──────────────┬───────────────┘  │
 └─────────────────────┼────────────────────────────────────┼──────────────────┘
                       │ HTTP POST /chat                    │ WhatsApp Web WebSocket
                       ▼                                    ▼
 ┌─────────────────────────────────────────┐ ┌─────────────────────────────────┐
 │       Web API Server (FastAPI)          │ │  WhatsApp Web Gateway v2.0      │
 │  - Pydantic v2 Schema Validation        │ │  (whatsapp_bridge/bridge.js)    │
 │  - Asynchronous Request Routing         │ │  - Headless Chromium Client     │
 │  - System Health & Dependency Probes    │ │  - Country Routing & Tag Strip  │
 └─────────────────────┬───────────────────┘ │  - Mobile Markdown Formatter    │
                       │                     └──────────────┬──────────────────┘
                       │ HTTP POST /chat (channel='whatsapp')│
                       └──────────────────┬─────────────────┘
                                          ▼
 ┌─────────────────────────────────────────────────────────────────────────────┐
 │                         RAG PIPELINE CORE ENGINE                            │
 │  1. Multilingual Detector: English, Bemba, Nyanja, Shona                    │
 │  2. Dense Vector Store: ChromaDB with BAAI/BGE-M3 Multilingual Embeddings   │
 │  3. Domain Isolation: Curated Statutory Filtering (ZRA, NRC, ZESCO, etc.)  │
 │  4. Multi-Provider LLM Cascade:                                             │
 │     - Primary: Google Gemini 3.5 Flash-Lite (High speed cloud)              │
 │     - Edge Fallback: Local Ollama with Qwen2.5:7b (Offline sovereign AI)    │
 │     - Third-line: OpenAI GPT-4o-mini                                        │
 │     - Failsafe: Grounded Context Excerpt                                    │
 │  5. Multilingual Translation: Meta NLLB-200 / Gemini 3.5 Flash              │
 └────────────────────────────────────────┬────────────────────────────────────┘
                                          │
                                          ▼
 ┌─────────────────────────────────────────────────────────────────────────────┐
 │                   EMPIRICAL EVALUATION & TAM DATABASE                       │
 │  - SQLite (`data/zedchatbot.db`)                                            │
 │  - Logs interaction channel ('web' vs 'whatsapp')                           │
 │  - Records user queries, detected language, retrieved sources, latency      │
 │  - Stores 1-5 star user feedback for Technology Acceptance Model analysis   │
 └─────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Core RAG Pipeline (`src/rag/pipeline.py`)

The pipeline serves as the central coordinator. It executes retrieval, invokes the generator cascade, translates output when required, and returns both the grounded answer and verifiable source citations.

```python
class RAGPipeline:
    """Handles the end-to-end RAG process with multilingual routing."""

    def __init__(self):
        self.vector_store = ZedVectorStore()
        self.retriever = ZedRetriever(self.vector_store)
        self.generator = ZedGenerator()

    def generate_reply(
        self,
        message: Optional[str] = None,
        country: str = "zm",
        language: Optional[str] = None,
        query: Optional[str] = None,
    ) -> Tuple[str, List[str]]:
        actual_message = message if message is not None else (query or "")
        clean_lang = language.strip().lower() if (language and isinstance(language, str)) else None
        
        # 1. Automatic Language Detection
        if not clean_lang or clean_lang == "auto":
            user_lang = detect_language(actual_message)
        else:
            user_lang = clean_lang

        # 2. Native Multilingual Vector Search (BGE-M3)
        try:
            docs = self.retriever.get_relevant_context(actual_message, country, top_k=4)
            if docs:
                context_text = self.retriever.format_docs(docs)
                sources = list(set([doc.metadata.get("source", "Unknown Source") for doc in docs]))
            else:
                return "I'm sorry, I don't have that specific official record in my database yet.", []
        except Exception as e:
            logger.error(f"Retrieval failed: {e}")
            context_text = ""
            sources = []

        # 3. Grounded Generation in English
        try:
            english_answer = self.generator.generate(actual_message, context_text, country, "en")
            final_answer = english_answer

            # 4. Translation into Target Local African Language
            if user_lang != "en":
                translated = translate_text(english_answer, source="en", target=user_lang)
                if translated:
                    final_answer = translated
        except Exception as e:
            logger.error(f"Generation failed: {e}")
            final_answer = "I encountered a technical error while processing your request."

        return final_answer, sources
```

---

## 3. Multilingual Dense Embeddings (`src/knowledge_base/vector_store.py`)

Employs **BAAI/BGE-M3**, a state-of-the-art multi-representation embedding model capable of processing cross-lingual and multilingual queries without intermediate machine translation.

```python
def _get_embeddings_instance():
    """Returns cached BAAI/BGE-M3 embeddings instance."""
    model_name = getattr(settings, "EMBEDDING_MODEL", "BAAI/bge-m3")
    return HuggingFaceEmbeddings(
        model_name=model_name,
        model_kwargs={"device": "cpu"},
        encode_kwargs={"normalize_embeddings": True},
    )

class ZedVectorStore:
    """Manages country-partitioned ChromaDB vector indices."""

    def get_vector_store(self, country_code: str) -> Chroma:
        persist_dir = f"./vector_store/{country_code.lower()}"
        return Chroma(
            persist_directory=persist_dir,
            embedding_function=self.embeddings,
            collection_name=f"zedchatbot_{country_code.lower()}",
        )
```

---

## 4. Multi-Provider Hybrid Generator Cascade (`src/rag/generator.py`)

Implements a four-tier provider cascade to guarantee zero downtime and eliminate single-point-of-failure vulnerabilities:

```
 Tier 1: Google Gemini 3.5 Flash-Lite (Ultra-fast Cloud Engine)
                         │
                         ▼ (On rate limit / cloud failure)
 Tier 2: Local Ollama Qwen2.5:7b (Sovereign Offline Edge LLM)
                         │
                         ▼ (On local resource exhaustion)
 Tier 3: OpenAI GPT-4o-mini (Auxiliary Cloud Backup)
                         │
                         ▼ (On catastrophic network failure)
 Tier 4: Grounded Context Excerpt (Zero-hallucination statutory fallback)
```

```python
class ZedGenerator:
    """Multi-provider generator with strict statutory grounding."""

    def generate(self, query: str, context: str, country: str, language: str) -> str:
        if not context or "No specific documents found" in context:
            return "I'm sorry, I don't have that specific official record in my database yet."

        # Cascade: Gemini -> Ollama -> OpenAI -> Context Excerpt
        if self.provider == "auto":
            # 1. Primary: Google Gemini
            res = self._invoke_gemini(query, context, country)
            if res:
                return res

            # 2. Edge Fallback: Local Ollama
            if self.ollama_llm:
                res = self._invoke_llm(self.ollama_llm, query, context, country)
                if res:
                    return res

            # 3. Third-line: OpenAI
            if self.openai_llm:
                res = self._invoke_llm(self.openai_llm, query, context, country)
                if res:
                    return res

        # 4. Grounded Context Failsafe
        if context:
            return f"According to official public records:\n\n{_clean_truncate(context, 600)}"

        return "I'm sorry, my AI brain is currently offline and no records were found."
```

---

## 5. Zero-Cost WhatsApp Web Gateway v2.0 (`whatsapp_bridge/bridge.js`)

Version 2.0 bypasses third-party sandbox restrictions and per-message USD costs by running a direct WhatsApp Web client backed by `whatsapp-web.js` and Headless Chromium:

```javascript
const { Client, LocalAuth } = require('whatsapp-web.js');

const client = new Client({
  authStrategy: new LocalAuth({ dataPath: './.wwebjs_auth' }),
  puppeteer: {
    headless: true,
    args: ['--no-sandbox', '--disable-setuid-sandbox', '--disable-dev-shm-usage']
  }
});

client.on('message', async (message) => {
  if (message.isStatus || message.fromMe || message.from.includes('@g.us')) return;

  const sender = message.from;
  const body = (message.body || '').trim();
  if (!body) return;

  // 1. Detect country from prefix or explicit tags
  let country = sender.startsWith('263') ? 'zw' : 'zm';
  let queryText = body;
  if (queryText.toLowerCase().startsWith('!zm') || queryText.toLowerCase().startsWith('!zw')) {
    country = queryText.slice(1, 3).toLowerCase();
    queryText = queryText.slice(3).trim();
  }

  // 2. Query ZedChatBot Backend Core
  const response = await fetch('http://127.0.0.1:8000/chat', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      message: queryText,
      country: country,
      language: 'auto',
      channel: 'whatsapp'
    })
  });

  const data = await response.json();
  const rawAnswer = data.answer || data.response || "I'm sorry, I couldn't find information on that.";

  // 3. Mobile Markdown Typography & Reply
  const formattedAnswer = formatForWhatsApp(rawAnswer);
  await message.reply(`${formattedAnswer}\n\n---\n*ZedChatBot | Community Assistant*`);
});

client.initialize();
```

---

## 6. Empirical Evaluation & TAM Logging (`src/core/database.py`)

To satisfy the academic research requirements of the final year capstone thesis, all interactions—regardless of whether they arrive via the web UI or WhatsApp—are logged to SQLite:

```python
class EvaluationDatabase:
    """Manages SQLite persistence for quantitative TAM analysis."""

    def log_interaction(
        self,
        channel: str,
        country: str,
        user_query: str,
        detected_language: str,
        retrieved_sources: List[str],
        response: str,
        response_time_ms: int,
    ) -> int:
        query = """
            INSERT INTO interactions (
                channel, country, user_query, detected_language,
                retrieved_sources, response, response_time_ms
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """
        # Inserts row and returns auto-generated interaction ID
        ...

    def record_feedback(self, interaction_id: int, rating: int, feedback_comment: str) -> bool:
        # Stores 1 to 5 star rating for TAM Perceived Usefulness & Ease of Use
        ...
```

---

## 7. Execution Commands

| Component | Command | Port / Target |
| :--- | :--- | :--- |
| **FastAPI Core Backend** | `python src/main.py` | `http://127.0.0.1:8000` |
| **WhatsApp Web Bridge v2.0** | `cd whatsapp_bridge && npm start` | `+260 953805423` |
| **Web User Interface** | Open browser at `http://127.0.0.1:8000` | Modern Glassmorphic Web UI |
| **ChromaDB Re-Ingestion** | `python src/knowledge_base/ingest.py` | Updates vector stores |
| **Unit & Integration Tests** | `pytest` | 19/19 Passing |

---
*Document Version 2.0 authored for final defense submission, University of Zambia (UNZA).*
