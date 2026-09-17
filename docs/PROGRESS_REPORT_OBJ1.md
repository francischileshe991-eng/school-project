# Progress Report: Research Objective One
**Project:** ZedChatBot for African Community
**Researcher:** Francis Chileshe
**Date:** May 2026

## 1. Objective Statement
"To design and implement a modular Retrieval-Augmented Generation (RAG) based conversational AI system that uses a curated Zambian knowledge base... supporting interaction via a web interface and WhatsApp in English, Bemba, and Nyanja, with a modular architecture that allows easy addition of knowledge bases for new countries."

## 2. Executive Summary of Implementation
As of May 2026, the foundational architecture of the ZedChatBot has been fully implemented and verified. The system successfully utilizes a **Native Multilingual RAG** approach, eliminating the need for intermediate translations and preserving the cultural and linguistic nuances of Bemba and Nyanja.

---

## 3. Modular System Architecture
The system is built using a decoupled, modular architecture to ensure maintainability and scalability.

| Module | Technology | Responsibility |
| :--- | :--- | :--- |
| **Orchestration** | LangChain | Manages the flow between data, embeddings, and LLM. |
| **Backend API** | FastAPI | High-performance asynchronous API handling Web and WhatsApp requests. |
| **Vector Store** | ChromaDB | Stores and retrieves document embeddings locally. |
| **Embeddings** | BAAI/BGE-M3 | Native multilingual semantic search (no translation required). |
| **Generator (LLM)** | Qwen2.5-7B | Locally hosted via Ollama; handles code-mixed multilingual replies. |
| **Translation Fallback** | Meta NLLB-200 | Provides safety-net translation for complex technical queries. |

---

## 4. Curated Zambian Knowledge Base
The system utilizes a "Zambia-First" knowledge base, curated from official government and educational sources.

*   **Government Services:** 
    *   **ZRA (Tax):** 2024 PAYE thresholds and TPIN registration.
    *   **Civic Identity:** NRC and Passport application requirements and costs.
*   **Health:**
    *   **NHIMA:** Contribution rates, benefits (Maternity/Neonatal), and registration.
    *   **Disease Guidance:** Prevention and treatment for Malaria and Cholera.
*   **Education:**
    *   **University Admissions:** General requirements for UNZA.
    *   **ECZ:** Online and SMS result checking procedures.
*   **Utilities:**
    *   **ZESCO:** 2024 Emergency Electricity Tariffs.
    *   **Water:** NWASCO-regulated connection requirements (NRC, Title Deeds).
*   **General Info:** Public holidays and emergency contact numbers (991, 992, 993, 909).

---

## 5. Multilingual Capabilities
ZedChatBot is designed to support **English, Bemba, and Nyanja** natively.

*   **Native Retrieval:** Using the **BGE-M3** model, the system can find English context for local language queries (Bemba/Nyanja) without intermediate translation.
*   **Native Generation:** The **Qwen2.5** model generates responses in the user's native tongue, supporting local dialects and conversational styles.

---

## 6. Interface and Integration
*   **Web Interface:** A fully functional, responsive HTML/CSS/JS frontend communicating with the `/chat` endpoint.
*   **WhatsApp Integration:** Scaffolded via Twilio API, supporting English, Bemba, and Nyanja interaction.
*   **Scalability:** Modular architecture allows adding new countries (e.g., `data/raw/zw/`) without code changes.

---

## 7. Results and Evidence
The system has been empirically tested and verified:
*   **Utility Inquiry (Nyanja):** Correctly identified the 2024 ZESCO emergency "Lifeline" tariff of K0.35.
*   **Civic Inquiry (Nyanja):** Correctly identified the 16+ age requirement for NRC application.
*   **Health Inquiry (English):** Correctly provided ORS/CTC guidance for Cholera.
*   **Tax Calculation (Nyanja):** Correctly calculated PAYE for an K8,000 salary.

---
**Status:** ✅ Objective One - Substantially Completed.
