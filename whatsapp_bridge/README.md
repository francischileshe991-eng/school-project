# ZedChatbot WhatsApp Web Bridge (Unofficial Direct Gateway)

This lightweight Node.js gateway links your local Zambian phone number (`+260 953805423`) directly to the ZedChatbot FastAPI RAG backend using [whatsapp-web.js](https://wwebjs.dev/).

---

## Key Advantages for University Defense & Demonstrations
1. **Zero Join Codes**: Unlike Twilio Sandbox, your examiners and lecturers do **not** need to type `join <code-word>`.
2. **Local Zambian Identity**: Users text a local Zambian number (`+260...`) instead of a US/UK Twilio number.
3. **Zero Expiration**: No 72-hour session expiration.
4. **Completely Free**: No credit card or per-message SMS costs.

---

## Prerequisites
- Node.js installed (v18+).
- The Python ZedChatbot server running:
  ```powershell
  python src/main.py
  ```

---

## How to Run

1. Open a new terminal in this folder:
   ```powershell
   cd "whatsapp_bridge"
   ```
2. Start the bridge:
   ```powershell
   npm start
   ```
   *(Or `node bridge.js`)*
3. A QR code will appear in the terminal.
4. On the phone with number `+260 953805423`:
   - Open **WhatsApp**.
   - Go to **Settings** (or the 3 dots menu on Android) ➔ **Linked Devices** ➔ **Link a Device**.
   - Scan the QR code in your terminal.
5. Once authenticated, the terminal will display:
   ```
   ✓ ZEDCHATBOT WHATSAPP BOT IS LIVE & READY!
   Linked Number: +260953805423
   ```
6. Anyone can now message `+260 953805423` on WhatsApp and immediately receive intelligent RAG answers from ZedChatbot!

---

## Architecture Flow

```
[ Citizen WhatsApp (+260...) ]
              │
              ▼ (WhatsApp Protocol)
[ WhatsApp Web Bridge (bridge.js) ]
              │
              ▼ (POST http://127.0.0.1:8000/chat)
[ ZedChatbot FastAPI RAG Backend ]
              │  • Multilingual Language Detector
              │  • BAAI/bge-m3 ChromaDB Retriever
              │  • LLM RAG Generator
              │  • SQLite Logging & TAM Stats
              ▼
[ Formatted Native Reply (• bullets, *bold*) ]
              │
              ▼
[ Citizen Receives Instant Response ]
```
