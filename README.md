# Zedchatbot for African Community

Zambia-first multilingual RAG chatbot scaffold.

## Initial scope

- Country: Zambia first
- Channels: Web first
- Languages: English first, then Bemba and Nyanja
- Domains: Government, education, utilities, health

## Structure

- `src/` application code
- `frontend/` simple static web interface
- `data/raw/` collected source documents by country
- `data/processed/` cleaned text by country
- `vector_store/` persisted vector database files
- `scripts/` ingestion and evaluation entry points
- `tests/` initial automated tests
- `docs/` report support and technical notes

## Quick start

1. Create a virtual environment.
2. Install the project in editable mode:

```bash
pip install -e ".[dev]"
```

For local multilingual translation with the NLLB model, install the translation extra:

```bash
pip install -e ".[dev,translation]"
```

3. Copy `.env.example` to `.env` and fill in values.
4. Run the API:

```bash
uvicorn src.main:app --reload
```

5. Open `frontend/index.html` in a browser.

The frontend expects the API to be reachable at `http://127.0.0.1:8000`.

Set `PRELOAD_PIPELINE_ON_STARTUP=true` in `.env` only if you want model warm-up during API startup.

## Next steps

- Collect trusted Zambian source documents
- Clean and chunk documents
- Build the vector index
- Connect retrieval to generation
- Replace the frontend placeholder with real API calls
