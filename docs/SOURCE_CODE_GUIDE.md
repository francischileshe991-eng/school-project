# Source Code Guide: Objective One Implementation (Version 1.0)
**Project:** ZedChatBot for African Community  
**Researcher:** Francis Chileshe  

> [!TIP]
> **Looking for the Complete End-to-End System Architecture (Version 2.0)?**  
> See **[Source Code & System Architecture Guide v2.0](file:///docs/SOURCE_CODE_GUIDE_v2.0.md)** for the full documentation covering the RAG pipeline, multi-provider hybrid cascade, WhatsApp Web Gateway v2.0, empirical TAM evaluation database, and the glassmorphic web UI.  
> *This document (v1.0) is preserved for historical Objective One milestone tracking.*

This document provide the core implementation logic for Objective One, demonstrating the modular RAG architecture and native multilingual capabilities.

---

## 1. Modular RAG Pipeline (`src/rag/pipeline.py`)
This is the "Brain" of the system. It demonstrates the **modular architecture** by coordinating the Retriever and the Generator without forcing translation.

```python
def generate_reply(self, message: str, country: str, language: str = None) -> Tuple[str, List[str]]:
    """Main entry point for Native Multilingual RAG."""
    # 1. Detect User Language (English, Bemba, or Nyanja)
    user_lang = language or detect_language(message)

    # 2. NATIVE SEARCH: BGE-M3 handles multilingual queries directly
    try:
        docs = self.retriever.get_relevant_context(message, country)
        context_text = self.retriever.format_docs(docs)
        sources = list(set([doc.metadata.get("source") for doc in docs]))
    except Exception as e:
        context_text = ""
        sources = []

    # 3. NATIVE GENERATION: Qwen2.5 responds in the detected language
    final_answer = self.generator.generate(message, context_text, country, user_lang)
    
    # 4. FALLBACK: Safety net if LLM fails native response
    if user_lang != "en" and self._needs_translation(final_answer, user_lang):
        translated = translate_text(final_answer, source="en", target=user_lang)
        if translated:
            final_answer = translated

    return final_answer, sources
```

---

## 2. Native Multilingual Embeddings (`src/knowledge_base/vector_store.py`)
Proves the use of **BGE-M3** for native multilingual retrieval, enabling the system to understand local languages without translation.

```python
def _get_embeddings_instance():
    """Returns cached embeddings instance (BGE-M3) for native multilingual support."""
    model_name = getattr(settings, "EMBEDDING_MODEL", "BAAI/bge-m3")
    # BGE-M3 is powerful and runs locally via HuggingFaceEmbeddings
    return HuggingFaceEmbeddings(
        model_name=model_name,
        model_kwargs={'device': 'cpu'},
        encode_kwargs={'normalize_embeddings': True}
    )

class ZedVectorStore:
    def get_vector_store(self, country_code: str) -> Chroma:
        """Initializes a ChromaDB instance per country for modularity."""
        persist_directory = f"./vector_store/{country_code.lower()}"
        return Chroma(
            persist_directory=persist_directory,
            embedding_function=self.embeddings,
            collection_name=f"zedchatbot_{country_code.lower()}",
        )
```

---

## 3. High-Precision Retrieval (`src/rag/retriever.py`)
Shows how the system isolates specific domains (ZRA, ZESCO, etc.) to fulfill the objective's requirement for a curated knowledge base.

```python
def get_relevant_context(self, query: str, country_code: str, threshold: float = 0.35) -> List[Document]:
    # 1. Search with Relevance Scores (0-1)
    results = self.vector_store.similarity_search_with_relevance(country_code, query, k=3)
    
    # 2. Threshold Filtering (Stricter matching for accuracy)
    relevant_docs = [doc for doc, score in results if score >= threshold]
    
    # 3. Domain Isolation (Automatically prioritizes ZESCO files if 'electricity' is mentioned, etc.)
    domains = {"zesco": "utilities", "zra": "government", "nhima": "health", "unza": "education"}
    # ... logic to filter docs by domain keyword ...
    return final_docs
```

---

## 4. Multi-Provider Hybrid Generation (`src/rag/generator.py`)
Demonstrates the multi-provider architecture supporting Google Gemini 3.8 Flash (primary high-speed cloud engine) with local Ollama (`qwen2.5:7b`) edge fallback and grounded factual failover.

```python
class ZedGenerator:
    def __init__(self):
        self.model_name = settings.MODEL_NAME  # qwen2.5:7b (local fallback)
        self.provider = settings.LLM_PROVIDER  # "gemini" (primary)
        self.system_prompt = (
            "You are an expert Zambian Community Assistant. "
            "Your task is to answer the user's question using ONLY the provided 'Context'. "
            "Answer immediately and directly in clean, well-formatted markdown in English."
        )

    def generate(self, query, context, country, language):
        # 1. Primary: Google Gemini 3.8 Flash (sub-second cloud inference)
        # 2. Edge Fallback: Local Ollama (Qwen2.5:7b offline inference)
        # 3. Tertiary Fallback: OpenAI GPT-4o-mini
        # 4. Zero-hallucination Fallback: Clean verbatim excerpt from official gazettes
        ...
```

---

## 5. Web Interface & API Integration (`src/api/web_api.py`)
Proves the "web interface" support requirement via a modern FastAPI backend.

```python
def create_app() -> FastAPI:
    app = FastAPI(title="Zedchatbot", version="v1")
    
    # Enable Web Access (CORS)
    app.add_middleware(CORSMiddleware, allow_origins=["*"])

    # Include Modular Routers for Web and WhatsApp
    app.include_router(web_router, tags=["Web"])
    app.include_router(whatsapp_router, tags=["WhatsApp"])
    
    return app
```

---

## 6. Curated Knowledge Base Structure
Data is curated from official 2024 sources and organized to allow easy expansion to new countries.

```text
data/raw/
├── zm/ (Zambia)
│   ├── government/ (NRC, Passport, ZRA Tax)
│   ├── education/  (UNZA, ECZ Results)
│   ├── utilities/  (ZESCO Tariffs, Water)
│   └── health/     (NHIMA, Malaria, Cholera)
└── zw/ (Zimbabwe)
    └── government/ (ZIMRA Tax Sample - Proof of Modularity)
```
