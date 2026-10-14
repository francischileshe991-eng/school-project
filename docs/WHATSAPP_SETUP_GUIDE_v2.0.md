# WhatsApp Gateway Integration Guide v2.0
**Project:** ZedChatBot for African Community  
**Author:** Francis Chileshe (Student ID: 2022014855)  
**Institution:** University of Zambia (UNZA) — Department of Computer Science  
**Supervisor:** Prof. J. Phiri  
**Version:** 2.0 (Production / Final Oral Defense Release)

> [!NOTE]
> **What's New in Version 2.0:**  
> Version 1.0 relied on Twilio's cloud sandbox, which required USD credits and mandatory `join <keyword>` sandbox activation.  
> **Version 2.0 introduces the Zero-Cost Direct Device Gateway (`whatsapp_bridge/bridge.js`)** powered by `whatsapp-web.js` and Headless Chromium. Any citizen or examiner can now send a normal WhatsApp message to your real phone number (**`+260 953805423`**) and immediately receive real-time, grounded RAG responses in English, Bemba, Nyanja, or Shona with **zero third-party subscription fees**.

---

## 1. Architectural Comparison: v1.0 vs v2.0

| Feature / Metric | Version 1.0 (Twilio Cloud Sandbox) | Version 2.0 (Direct WhatsApp Web Gateway) |
| :--- | :--- | :--- |
| **Connection Mechanism** | Twilio REST API + Public ngrok Webhook | Direct WhatsApp Web WebSocket via Headless Chromium |
| **Phone Number Display** | US Sandbox Number (`+1 415 523 8886`) | **Real Local Number (`+260 953805423`)** |
| **Join Keyword Required?** | **Yes** (e.g., `join bagged-wipe`) | **No** (Direct natural chat by anyone) |
| **Cost / Message Fees** | ~$0.005 - $0.05 per msg (USD) | **$0.00 (Completely Free & Open-Source)** |
| **Session Lifetime** | 72 hours per sandbox opt-in | **Persistent** (Saved via `.wwebjs_auth`) |
| **External Dependencies** | Twilio Cloud, ngrok Tunnel | Node.js runtime, Local Chromium |
| **Evaluation Logging** | `channel="whatsapp"` in SQLite | `channel="whatsapp"` in SQLite |
| **Oral Defense Viability** | Restricted (Examiners must type join codes) | **Optimal (Examiners text directly from their phones)** |

---

## 2. Version 2.0 System Architecture

```
 ┌─────────────────────────────────────────────────────────────┐
 │           Citizen / Examiner Mobile Phone on WhatsApp       │
 └──────────────────────────────┬──────────────────────────────┘
                                │ Natural WhatsApp Chat
                                ▼
 ┌─────────────────────────────────────────────────────────────┐
 │       WhatsApp End-to-End Encrypted Cloud Infrastructure    │
 └──────────────────────────────┬──────────────────────────────┘
                                │ WebSocket Multi-Device Protocol
                                ▼
 ┌─────────────────────────────────────────────────────────────┐
 │    Local WhatsApp Bridge Gateway (`whatsapp_bridge/`)       │
 │    - whatsapp-web.js runtime running on Node.js             │
 │    - Headless Chromium with LocalAuth (`.wwebjs_auth/`)     │
 │    - Auto-detects country prefix (+260 -> zm, +263 -> zw)   │
 │    - Strips routing tags (!zm / !zw)                        │
 └──────────────────────────────┬──────────────────────────────┘
                                │ HTTP POST http://127.0.0.1:8000/chat
                                │ { message, country, language: 'auto', channel: 'whatsapp' }
                                ▼
 ┌─────────────────────────────────────────────────────────────┐
 │             ZedChatBot FastAPI RAG Core (`src/`)            │
 │                                                             │
 │  1. Multilingual Detector: Identifies en, bem, ny, or sn    │
 │  2. ChromaDB Dense Vector Search: BAAI/BGE-M3 (Top-4 docs)  │
 │  3. Curated Statutory Domain Isolation (ZRA, NRC, ZESCO...) │
 │  4. Hybrid Generation: Gemini 3.8 Flash / Qwen2.5 Edge │
 │  5. Multilingual Translation: Meta NLLB-200 / Gemini        │
 │  6. Evaluation Logging: SQLite DB (`data/zedchatbot.db`)    │
 └──────────────────────────────┬──────────────────────────────┘
                                │ JSON Response { answer, sources, interaction_id }
                                ▼
 ┌─────────────────────────────────────────────────────────────┐
 │    Mobile Markdown Formatter (`bridge.js:formatForWhatsApp`)│
 │    - Headers (###) converted to WhatsApp *BOLD TITLES*      │
 │    - Markdown bold (**word**) converted to WhatsApp *word*  │
 │    - Dashes converted to clean bullet dots (•)              │
 │    - Generates step-by-step spacing for small screens       │
 └──────────────────────────────┬──────────────────────────────┘
                                │
                                ▼
                 Delivered back to User WhatsApp Chat
```

---

## 3. Quickstart: Running the Version 2.0 Bridge

### Step 3.1: Start the ZedChatBot Backend Server
In your main repository directory, ensure the Python FastAPI backend is active:
```powershell
python src/main.py
```
*Verify output confirms: `INFO: Application startup complete. Uvicorn running on http://127.0.0.1:8000`.*

### Step 3.2: Start the WhatsApp Web Bridge
Open a second PowerShell terminal:
```powershell
cd whatsapp_bridge
npm start
```
*(Alternatively: `node bridge.js`)*

### Step 3.3: Link Device (First-Time Only)
1. If this is the first run, the terminal will render an ASCII QR code.
2. Open WhatsApp on your primary phone (**`+260 953805423`**).
3. Navigate to: **Settings** ➔ **Linked Devices** ➔ **Link a Device**.
4. Scan the QR code displayed in the terminal.
5. Once authenticated, the terminal will display:
   ```text
   ✓ WhatsApp authentication successful! Initializing session...
   ====================================================
     ✓ ZEDCHATBOT WHATSAPP BOT IS LIVE & READY!
     Linked Number: +260953805423
     Anyone who sends a message to this number will get
     real-time RAG answers from ZedChatbot AI.
   ====================================================
   ```

> [!TIP]
> **Subsequent Restarts are Instant:**  
> The session token is permanently cached in `whatsapp_bridge/.wwebjs_auth`. You will **never** need to re-scan the QR code when restarting the bridge unless you explicitly tap "Log out" inside your phone's WhatsApp settings.

---

## 4. Operational Features in Version 2.0

### 4.1 Automatic Country Detection & Explicit Tag Overrides
The bridge inspects the sender's international dialing prefix automatically:
- Senders starting with **`+260`** (or international numbers) route to Zambia records (**`zm`**).
- Senders starting with **`+263`** route to Zimbabwe records (**`zw`**).
- **Explicit Directive Tags**: Citizens can prepend `!zm` or `!zw` to query cross-border public records:
  - Example: `!zw What are the passport fees in Zimbabwe?`
  - The bridge automatically routes to `zw` and strips the `!zw` prefix before sending the query to the vector retriever.

### 4.2 Native Multilingual Conversations
The RAG pipeline detects whether the question is phrased in **English**, **icibemba**, **chiNyanja**, or **chiShona**:
- Queries asked in Bemba (e.g., *"Kuti napoka shani NRC?"*) receive grounded step-by-step guidance translated cleanly into Bemba.
- Statutory acronyms (NRC, ZRA, TPIN, ZESCO, CDF, NHIMA) are preserved without distortion.

### 4.3 Clean Mobile Typography
Standard Markdown output from LLMs can look broken on mobile WhatsApp. The v2.0 bridge includes a dedicated `formatForWhatsApp()` filter that:
- Replaces markdown `**bold**` with single-asterisk `*bold*`.
- Replaces markdown headers (`### Procedure`) with `*PROCEDURE*`.
- Replaces raw hyphens (`- `) with legible unicode bullets (`• `).
- Enforces double line-breaks before numbered steps (`Step 1:`, `Step 2:`) for enhanced legibility on small phone screens.
- Appends an official bot signature: `--- \n *ZedChatBot | Community Assistant*`.

### 4.4 Empirical TAM Logging (`data/zedchatbot.db`)
Every message processed through the v2.0 bridge automatically logs to the central SQLite evaluation database:
- `channel`: `"whatsapp"` (enabling direct comparative analysis against the `"web"` channel for your Technology Acceptance Model findings).
- `country`: `"zm"` or `"zw"`.
- `user_query`: Exact question submitted.
- `detected_language`: `"en"`, `"bem"`, `"ny"`, or `"sn"`.
- `retrieved_sources`: File paths of official gazettes/documents retrieved.
- `response_time_ms`: End-to-end latency in milliseconds.

---

## 5. Demonstration Test Suite for Oral Defense

Use this curated test script during your final project defense to showcase the capabilities to your examination committee:

| Test Case | Language | Query to Send on WhatsApp | Expected Statutory Behavior |
| :--- | :--- | :--- | :--- |
| **Civic (NRC)** | English | *"How do I get an NRC in Zambia?"* | Step 1: 16+ age rule, Step 2: Clinic card / birth cert & parent NRC, Free of charge. |
| **Energy (ZESCO)**| English | *"What are the 2026 ZESCO electricity tariffs?"*| Explains progressive multi-tier block tariff system and lifeline allocation. |
| **Education (CBU)**| English | *"How do I apply for Copperbelt University?"* | Directs to online portal, 5 O-levels requirement, non-refundable fee. |
| **Civic (Bemba)** | icibemba | *"Kuti napoka shani NRC?"* | Full step-by-step NRC instructions rendered naturally in icibemba. |
| **Civic (Nyanja)**| chiNyanja| *"Kodi ndingatenge bwanji NRC?"* | Step-by-step NRC requirements rendered naturally in chiNyanja. |
| **Cross-Border** | English | *"!zw What are the passport fees in Zimbabwe?"* | Identifies Zimbabwe jurisdiction, cites official USD statutory passport rates. |
| **Hallucination** | English | *"Can I apply for a driver's license at age 12?"*| Politely denies with statutory grounds: minimum driving age is 18 years. |

---

## 6. Troubleshooting & Maintenance

### What if the bridge says `Backend returned HTTP 500`?
Ensure your Python server is running in your first terminal window:
```powershell
python src/main.py
```
Test that the local endpoint is responsive:
```powershell
curl http://127.0.0.1:8000/health
```

### What if I need to run WhatsApp from a different computer or phone?
Delete the `.wwebjs_auth` session directory:
```powershell
Remove-Item -Recurse -Force whatsapp_bridge\.wwebjs_auth
```
Restart `node bridge.js` and scan the newly generated QR code.

### How do I view live interaction metrics in SQLite?
Run the following PowerShell command to inspect recent WhatsApp queries:
```powershell
python -c "from src.core.database import db; rows = db.get_recent_interactions(limit=5); [print(f'#{r[\"id\"]} [{r[\"channel\"]}] {r[\"user_query\"]} -> {r[\"response_time_ms\"]}ms') for r in rows]"
```

---
*Document Version 2.0 finalized for the Department of Computer Science, University of Zambia.*
