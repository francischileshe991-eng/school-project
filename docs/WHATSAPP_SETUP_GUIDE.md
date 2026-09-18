# Twilio WhatsApp Integration & Live Demonstration Guide (Version 1.0)

> [!TIP]
> **Looking for Version 2.0 (Zero-Cost Direct WhatsApp Web Gateway)?**  
> See the updated **[WhatsApp Gateway Integration Guide v2.0](file:///docs/WHATSAPP_SETUP_GUIDE_v2.0.md)** for connecting directly to your real Zambian phone number (`+260 953805423`) without Twilio fees, sandbox join codes, or USD costs.  
> *This document (v1.0) is preserved as an alternative cloud-hosted deployment option.*

This guide provides the exact steps to connect **Zedchatbot for African Community** to WhatsApp via Twilio's WhatsApp Sandbox for live messaging, testing, and your final oral defense demonstration.

---

## 1. System Architecture Overview

```
 [User's Phone on WhatsApp]
            │
            ▼ (Encrypted WhatsApp message)
 [Twilio Cloud Sandbox: +1 415 523 8886]
            │
            ▼ (HTTP POST webhook over secure tunnel)
 [ngrok Public Tunnel: https://bagged-wipe-gradually.ngrok-free.dev/whatsapp]
            │
            ▼ (Forwarded to localhost:8000)
 [Zedchatbot FastAPI Application]
            │
            ├── 1. Language Detector (English, Bemba, Nyanja, Shona)
            ├── 2. Immediate TwiML ACK ("Thinking..." in user's language)
            ├── 3. BGE-M3 Multilingual Vector Search (ChromaDB)
            ├── 4. Grounded Response Generation (LLM Cascade)
            ├── 5. NLLB-200 Translation (if local African language)
            └── 6. Interaction Logged to SQLite (data/zedchatbot.db)
            │
            ▼ (Twilio REST API: client.messages.create)
 [Twilio Cloud Gateway]
            │
            ▼
 [User's Phone Receives Grounded Response on WhatsApp]
```

---

## 2. Prerequisites & Credentials

Your `.env` file is already authenticated with your active Twilio account:
- **Twilio Account Name**: `ZEDchatbot` (Status: `Active`)
- **Account SID**: `AC89645d0ef202c1e06642850159fe4bc6`
- **Auth Token**: *(configured in `.env`)*
- **Twilio WhatsApp Number**: `+1 415 523 8886`

---

## 3. Step-by-Step Connection Instructions

### Step 3.1: Start the Backend Server & Public Tunnel
1. **Ensure the Zedchatbot server is running**:
   ```powershell
   python src/main.py
   ```
   *(Server starts on `http://127.0.0.1:8000`)*

2. **Ensure the ngrok public tunnel is running**:
   ```powershell
   ngrok http 8000
   ```
   Your active public tunnel URL is currently:
   ```
   https://bagged-wipe-gradually.ngrok-free.dev
   ```

---

### Step 3.2: Configure Webhook in Twilio Console
1. Open your browser and navigate to the **[Twilio Console](https://console.twilio.com/)**.
2. In the left navigation menu or search bar, navigate to:
   - **Messaging** ➔ **Try it out** ➔ **Send a WhatsApp message**
   - Alternatively: **Messaging** ➔ **Settings** ➔ **WhatsApp sandbox settings**
3. Locate the configuration section labeled:
   **"WHEN A MESSAGE COMES IN"**
4. Enter your public webhook URL:
   ```
   https://bagged-wipe-gradually.ngrok-free.dev/whatsapp
   ```
5. Set the HTTP request method dropdown to:
   **`HTTP POST`**
6. Click **Save** at the bottom of the page.

---

### Step 3.3: Connect Your Phone to the Twilio Sandbox
1. On the same Twilio WhatsApp Sandbox page, note your unique sandbox join phrase (e.g., `join <keyword-here>`).
2. Open WhatsApp on your personal phone or WhatsApp Web.
3. Start a new chat with Twilio's WhatsApp number: **`+1 415 523 8886`**.
4. Send the join message:
   ```
   join <your-sandbox-keyword>
   ```
5. Twilio will reply with a confirmation message:
   > *"You are all set! The sandbox is now configured to message with your phone."*

---

## 4. Testing Queries for Oral Defense Demonstration

Once connected, test queries directly in WhatsApp across multiple domains and languages:

### Test 1: Government / Civic Services (English)
- **Send**: `How do I apply for a Zambian passport?`
- **Expected Behavior**:
  1. Immediate prompt acknowledgment: *"Thank you! I'm thinking about your question and will reply shortly..."*
  2. Final reply detailing requirements, fee (K300 ordinary / K500 express), and the e-Services portal (`www.gsb.gov.zm`).

### Test 2: Local Language Civic Query (Bemba)
- **Send**: `Mwapoleni, bushe kuti napata shani passport?`
- **Expected Behavior**:
  1. Immediate Bemba acknowledgment: *"Natotela! Ndetontokania pe lipusho lwenu, nalayasuka mukashita kanoono"*
  2. Final grounded response delivered in fluent Bemba.

### Test 3: Local Language Civic Query (Nyanja)
- **Send**: `Kodi ndingatenge bwanji NRC ku Lusaka?`
- **Expected Behavior**:
  1. Immediate Nyanja acknowledgment: *"Zikomo! Ndikuganiza za funso lanu ndipo ndiyankha posachedwa..."*
  2. Final grounded response in Nyanja citing the Department of National Registration.

### Test 4: Utility Inquiries (Electricity / ZESCO)
- **Send**: `What are the current ZESCO tariffs for residential customers?`
- **Expected Behavior**:
  - Accurate breakdown of R1 (0-100 kWh @ K0.47), R2 (101-300 kWh @ K0.85), and R3 (>300 kWh @ K1.94).

---

## 5. Verifying Interaction Logging (TAM Research Data)

Every question sent over WhatsApp is automatically stored in the local SQLite evaluation database with `channel = 'whatsapp'`.

To verify logged interactions after a WhatsApp session:
```powershell
python -c "from src.core.database import db; import json; print(json.dumps(db.get_stats(), indent=2))"
```
Output will confirm interactions grouped by channel (`whatsapp`), country (`zm`), and detected languages (`en`, `bem`, `ny`, `sn`).
