# Architecture

Zedchatbot uses a simple RAG flow:

1. User sends a query through the web interface.
2. The API receives the query and country/language context.
3. The retriever will search a country-specific vector store.
4. The generator will answer using retrieved context.
5. The response is returned with source references.

The first implementation target is Zambia.
