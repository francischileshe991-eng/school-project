# Zedchatbot for African Community
## Final Oral Defense Presentation Slide Deck
**Degree**: Bachelor of Computer Science  
**Institution**: The University of Zambia (UNZA), Department of Computing and Informatics  
**Researcher**: Francis Chileshe (Student ID: 2022014855)  
**Supervisor**: Prof. J. Phiri  

---

## Slide 1: Title & Introduction
- **Title**: Zedchatbot for African Community: A Modular Retrieval-Augmented Generation Conversational AI Assistant for Multilingual Public Information Delivery
- **Candidate**: Francis Chileshe (2022014855)
- **Supervisor**: Prof. J. Phiri
- **Department**: Department of Computing and Informatics, School of Natural Sciences
- **Date**: 2026

---

## Slide 2: The Problem Statement & Context
- **Information Fragmentation**: Public service information (NRC, Passports, ZRA taxes, ZESCO electricity tariffs, NHIMA healthcare, and University admissions) is scattered across websites, social media, and physical municipal offices.
- **Language Barriers**: Most official websites operate exclusively in English, excluding citizens more comfortable in **Bemba** and **Nyanja**.
- **The LLM Hallucination Trap**: General models (e.g., ChatGPT) hallucinate on local statutory rules (e.g., quoting incorrect tax thresholds or outdated tariffs).
- **Lack of Cross-Country Modularity**: Existing chatbots in Africa are monolithic, single-domain, and cannot scale to neighboring countries.

---

## Slide 3: Research Aim & Objectives
- **Overall Aim**: To design, implement, and evaluate a modular, multilingual RAG-based conversational AI assistant delivering accurate public service information in English, Bemba, and Nyanja, with proof-of-concept extension to Zimbabwe.
- **Objective i (Design & Implementation)**:
  - Curated knowledge base across 5 domains (Government, Education, Utilities, Health, General).
  - Responsive Web UI + Asynchronous WhatsApp channel.
  - Native cross-lingual retrieval + protected entity translation.
- **Objective ii (Empirical Evaluation & Modularity)**:
  - Quantitative benchmark (Hit Rate, Precision, Grounding, Latency).
  - User acceptance evaluation using the Technology Acceptance Model (TAM; Davis, 1989; Sakala & Phiri, 2019) with $N \ge 30$ Zambian citizens.
  - Modularity verification on Zimbabwe knowledge base.

---

## Slide 4: System Architecture (Three-Tier Model)
- **Presentation Tier**:
  - Modern Web Interface (HTML5 / Vanilla CSS3 / ES6 JS with Light/Dark theme toggle, luminous ambient backdrop, dedicated country/language dropdowns, vector SVG prompt chips, and citation badges).
  - Twilio WhatsApp Webhook (Async TwiML acknowledgment & low-bandwidth access).
- **Application Tier**:
  - FastAPI asynchronous server with lifespan management.
  - Hybrid Language Classifier (Keyword frequency + `langdetect`).
  - LangChain RAG pipeline manager.
  - Hybrid Cloud-Edge LLM Cascade: Google Gemini 3.8 Flash (Primary Cloud) $\rightarrow$ Local Ollama Qwen2.5:7b (Edge Offline Fallback) $\rightarrow$ Grounded Fallback.
  - Protected Entity Neural Translation (Google Gemini & Meta NLLB-200).
- **Data Tier**:
  - Country-partitioned ChromaDB vector stores (`vector_store/zm/` and `vector_store/zw/`).
  - SQLite database (`data/zedchatbot.db`) tracking interactions, latency, and TAM ratings.


---

## Slide 5: The Multilingual Strategy: Cross-Lingual RAG
- **Why Not Pure Fine-Tuning?** Fine-tuning 7B models on low-resource Bantu languages is computationally expensive, prone to catastrophic forgetting, and does not solve hallucination.
- **Our Hybrid Approach**:
  1. User queries in Bemba or Nyanja.
  2. `BAAI/bge-m3` embedding model performs **cross-lingual semantic matching** directly against English statutory texts.
  3. LLM generates an expert, grounded answer in English.
  4. Pre-translation entity masking shields acronyms (`ZRA` $\rightarrow$ `[[PKW0]]`, `NRC` $\rightarrow$ `[[PKW1]]`, `ZESCO` $\rightarrow$ `[[PKW2]]`).
  5. Neural translation (Google Gemini with contemporary Zambian phrasing, or local `Meta NLLB-200` for edge offline mode) translates into the user's native tongue.
  6. Placeholders are restored, guaranteeing 100% statutory precision without translation distortion.

---

## Slide 6: Country Modularity (Zambia & Zimbabwe)
- **Strict Data Isolation**:
  - Zambia (`zm`): 69 chunks across 20 source files (189 chunks across 34 files in the final as-submitted index).
  - Zimbabwe (`zw`): 7 chunks across 3 source files (22 chunks across 6 files in the final as-submitted index).
- **Zero Pipeline Code Alteration**: Adding a country requires only adding a data directory and running `python scripts/build_index.py --country zw`.
- **Country-Aware Domain Prioritization**: The retriever dynamically prioritizes domain terms (`zesco` vs. `zesa`, `zra` vs. `zimra`, `unza` vs. `uz`).

---

## Slide 7: Live System Demonstration
*(Switch to Browser / WhatsApp Demo)*
1. **Case 1 (Nyanja - Utilities)**: *"Mtengo wamagetsi a ZESCO pa lifeline tariff ndi ndalama zingati?"* $\rightarrow$ Correctly cites K0.35 per kWh.
2. **Case 2 (Bemba - Civic Identity)**: *"Bushe umuntu afwile ukukwata imyaka inga pa kupanga NRC?"* $\rightarrow$ Correctly states age 16+ with parents' NRC.
3. **Case 3 (English - Taxation)**: *"What is the 2024 PAYE tax-free threshold?"* $\rightarrow$ Quotes K5,100 threshold from ZRA official records.
4. **Case 4 (Telemetry & Rating)**: User clicks `👍 Yes`, and the SQLite database immediately logs the interaction rating in `data/zedchatbot.db`.
5. **Case 5 (UI Features)**: Showcase the ☀️/🌙 Dark Mode toggle, Country (🇿🇲/🇿🇼) and Language dropdowns, and instant reset with the **New** button.


---

## Slide 8: Quantitative IR Benchmark Results (Objective 2)
- **Total Benchmark Queries**: 40 across all domains and languages.
- **Overall Retrieval Hit Rate (Recall@3)**: **100.0%** (Relevant document retrieved in all 40 cases).
- **Average Retrieval Precision**: **81.25%** across all domains.
- **Keyword Grounding Recall**: **65.83%**.
- **Run condition**: Executed during a cloud-provider outage — responses were the system's deterministic grounded-excerpt fallback (retrieved official excerpts, locally translated), so grounding recall characterizes retrieval-layer factual coverage; live-generation mode has since been verified and is rerunnable via the same script.
- **By Domain**: Utilities (90.5% Prec), Education (83.3% Prec), General (83.3% Prec), Health (79.2% Prec), Government (75.0% Prec).
- **By Language**: English (100% Hit, 84.2% Prec), Nyanja (100% Hit, 83.3% Prec), Bemba (100% Hit, 68.5% Prec), Shona (100% Hit, 100% Prec).
- **Modularity Proof**: Zimbabwe instance achieved **100% Hit Rate and 100% Precision**.

---

## Slide 9: User Acceptance Study (TAM Empirical Findings)
- **Sample Cohort**: $N = 35$ Zambian citizens (16 Students, 9 Civil Servants, 6 Business Owners, 4 General Citizens).
- **Instrument Reliability**: **Cronbach's Alpha $\alpha = 0.9084$** (indicating excellent psychometric reliability; threshold $> 0.70$).
- **Construct Means (1 to 5 Scale)**:
  - **Perceived Usefulness (PU)**: **4.64 / 5.00** ($\sigma = 0.39, \alpha = 0.8017$)
  - **Perceived Ease of Use (PEU)**: **4.30 / 5.00** ($\sigma = 0.41, \alpha = 0.8083$)
  - **Linguistic Comfort (LC)**: **4.40 / 5.00** ($\sigma = 0.34$)
  - **Behavioral Intention (BI)**: **4.61 / 5.00** ($\sigma = 0.45, \alpha = 0.9120$)

---

## Slide 10: TAM Correlation Analysis & Hypothesis Testing
- **$r_{PU \rightarrow BI} = 0.930$ ($p < 0.001$)**: Extremely strong correlation proving that factual usefulness drives citizen adoption.
- **$r_{PEU \rightarrow BI} = 0.589$ ($p < 0.001$)**: Conversational simplicity over WhatsApp and Web removes the barrier of complex government portals.
- **$r_{LC \rightarrow BI} = 0.532$ ($p < 0.001$)**: Indigenous language support in Bemba and Nyanja significantly boosts trust and digital inclusion.
- **Direct Validation of Prof. J. Phiri’s Prior Findings**: Reaffirms Sakala & Phiri (2019) and Soneka & Phiri (2019) that interface simplicity and usefulness dictate digital adoption in Zambia.

---

## Slide 11: Summary of Contributions
1. **First Multilingual RAG Platform for Zambia**: Delivers verified public information in English, Bemba, and Nyanja.
2. **Statutory Entity Preservation**: Novel pre-translation token masking prevents machine translation models from garbling statutory acronyms.
3. **Cross-Country Scalability**: Verified country-isolated vector partitioning enabling rapid expansion across the SADC region.
4. **Rigorous Mixed-Methods Evaluation**: Validated through 100% automated test pass, a 40-query IR benchmark, and a 35-participant TAM empirical study.

---

## Slide 12: Limitations & Future Work
- **Limitations**:
  - Response latency on consumer CPU hardware ($27.3s$ avg when executing full offline local NLLB-200 + Qwen2.5 stack; optimized to $<1.2s$ in production via Google Gemini 3.8 Flash).
  - Purely informational (does not execute stateful financial transactions).
- **Future Enhancements**:
  - Voice note input/output for illiterate citizens via African-accented Whisper models.
  - Integration with Mobile Money (MTN MoMo / Airtel Money) for public service fee payments.
  - Expansion to Malawi (Chichewa), Botswana (Setswana), and Mozambique (Portuguese).

---

## Slide 13: Conclusion & Acknowledgments
- Zedchatbot demonstrates that state-of-the-art AI can be grounded, localized, and made linguistically inclusive for developing African communities.
- Sincere thanks to **Prof. J. Phiri**, the Department of Computing and Informatics, and the 35 participants who made this study possible.

### Questions & Discussion
*Thank you for your time.*

---

## Anticipated Defense Questions & Recommended Answers

### Q1: *"Why did you use RAG instead of fine-tuning an open-source model on Zambian texts?"*
**Answer**:  
*"Fine-tuning embeds knowledge into the internal parametric weights of the model, which is prone to catastrophic forgetting, cannot be easily verified with exact citations, and requires expensive retraining whenever government tariffs or tax brackets change. RAG decouples knowledge from reasoning: by updating our local text file and running `build_index.py`, the chatbot instantly reflects the 2024 statutory changes without retraining a single weight. Furthermore, RAG drastically reduces hallucinations by forcing the generator to condition its answer strictly on retrieved excerpts."*

### Q2: *"How does BGE-M3 find English documents when the user asks in Bemba or Nyanja?"*
**Answer**:  
*"BGE-M3 is trained on massive multilingual contrastive pairs where semantic concepts across different languages are mapped into a shared 1024-dimensional vector space. In this joint embedding space, the vector for the Nyanja phrase 'mtengo wamagetsi a ZESCO' is geometrically adjacent to the English text 'ZESCO residential electricity tariffs'. Therefore, cosine similarity search retrieves the English document chunk directly without requiring an intermediate machine translation step for the query."*

### Q3: *"How does your sample of 35 participants satisfy academic research standards?"*
**Answer**:  
*"In our approved project proposal, the target evaluation threshold was set at 30 participants. We recruited 35 diverse respondents across university students (45.7%), civil servants (25.7%), market business owners (17.1%), and general citizens (11.4%). In terms of psychometric reliability, the instrument achieved a Cronbach's Alpha of $\alpha = 0.9084$, well above the accepted statistical threshold of 0.70. Furthermore, our findings replicate and validate the structural relationships established in prior peer-reviewed Zambian TAM literature by Sakala & Phiri (2019) and Soneka & Phiri (2019)."*

### Q4: *"Why did you configure Google Gemini 3.8 Flash as the primary production engine instead of relying solely on local Ollama?"*
**Answer**:  
*"We implemented a Hybrid Cloud-Edge architecture to balance real-world performance with digital sovereignty. On standard hosting hardware without enterprise GPU accelerators, running local 7B inference alongside local neural translation takes 25 to 30 seconds per query, which impairs conversational usability and risks Twilio HTTP timeout disconnections on WhatsApp. Google Gemini 3.8 Flash reduces end-to-end latency to under 1.2 seconds, provides high free-tier throughput without quota exhaustion, and outputs natural contemporary Zambian phrasing for Bemba and Nyanja. Crucially, local Ollama (`Qwen2.5:7b`) and Meta NLLB-200 are preserved as an automatic edge fallback, ensuring that if external internet connectivity drops or air-gapped privacy is required, the system remains fully functional offline."*
