/**
 * ZedChatbot WhatsApp Web Bridge (Unofficial Direct Gateway)
 * 
 * Uses whatsapp-web.js to connect any standard WhatsApp account (+260...)
 * directly to the ZedChatbot FastAPI RAG backend without Twilio, sandbox codes,
 * or USD costs.
 * 
 * Usage:
 *   1. Ensure FastAPI server is running: python src/main.py
 *   2. Run this bridge: npm start (or node bridge.js)
 *   3. Scan the terminal QR code using WhatsApp on your phone (+260953805423)
 *      (WhatsApp -> Settings -> Linked Devices -> Link a Device)
 */

const { Client, LocalAuth } = require('whatsapp-web.js');
const qrcode = require('qrcode-terminal');

const BACKEND_URL = process.env.BACKEND_URL || 'http://127.0.0.1:8000';

console.log('====================================================');
console.log('  ZedChatbot WhatsApp Web Bridge Starting...');
console.log(`  Target Backend: ${BACKEND_URL}`);
console.log('====================================================\n');

const fs = require('fs');

function getBrowserExecutablePath() {
  const chromePath = 'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe';
  const edgePath = 'C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe';
  if (fs.existsSync(chromePath)) return chromePath;
  if (fs.existsSync(edgePath)) return edgePath;
  return undefined;
}

const execPath = getBrowserExecutablePath();
if (execPath) {
  console.log(`  Using Browser Engine: ${execPath}`);
}

// Configure client with persistent local session storage
const client = new Client({
  authStrategy: new LocalAuth({
    dataPath: './.wwebjs_auth'
  }),
  webVersionCache: {
    type: 'none'
  },
  puppeteer: {
    headless: true,
    executablePath: execPath,
    args: [
      '--no-sandbox',
      '--disable-setuid-sandbox',
      '--disable-dev-shm-usage',
      '--disable-accelerated-2d-canvas',
      '--no-first-run',
      '--no-zygote',
      '--disable-gpu'
    ]
  }
});

console.log('  Initializing WhatsApp client & loading web session...\n');

// Format markdown text for native WhatsApp readability
function formatForWhatsApp(text) {
  if (!text) return '';
  let s = String(text).replace(/\r\n/g, '\n');

  // Convert markdown headers to bold titles
  s = s.replace(/^#{1,4}\s*(.*?)$/gm, '*$1*');

  // Convert **bold** to *bold*
  s = s.replace(/\*\*([^*]+)\*\*/g, '*$1*');

  // Convert bullet markers to clean dots
  s = s.replace(/^(\s*)[-*]\s+/gm, '$1• ');

  // Double newline before step headers
  s = s.replace(/(?<!\n)\n(\*?Step\s+\d+[:\)])/gi, '\n\n$1');

  // Collapse excessive blank lines
  s = s.replace(/\n{3,}/g, '\n\n');

  return s.trim();
}

// 1. Event: QR Code Received
client.on('qr', (qr) => {
  console.log('\n====================================================');
  console.log('SCAN THIS QR CODE TO LINK YOUR WHATSAPP BOT:');
  console.log('1. Open WhatsApp on your phone (+260 953805423)');
  console.log('2. Tap Settings -> Linked Devices -> Link a Device');
  console.log('3. Point your camera at the QR code below:');
  console.log('====================================================\n');
  qrcode.generate(qr, { small: true });
});

// 2. Event: Authenticated
client.on('authenticated', () => {
  console.log('✓ WhatsApp authentication successful! Initializing session...');
});

// 3. Event: Authentication Failure
client.on('auth_failure', (msg) => {
  console.error('✗ Authentication failure:', msg);
});

// 4. Event: Ready to receive messages
client.on('ready', () => {
  const number = client.info ? client.info.wid.user : 'Unknown';
  console.log('\n====================================================');
  console.log(`  ✓ ZEDCHATBOT WHATSAPP BOT IS LIVE & READY!`);
  console.log(`  Linked Number: +${number}`);
  console.log(`  Anyone who sends a message to this number will get`);
  console.log(`  real-time RAG answers from ZedChatbot AI.`);
  console.log('====================================================\n');
});

// 5. Event: Incoming Message
client.on('message', async (message) => {
  try {
    // Ignore status updates, broadcast messages, and messages sent by the bot itself
    if (message.isStatus || message.fromMe) return;
    if (message.from.includes('status@broadcast')) return;

    const sender = message.from;
    const body = (message.body || '').trim();

    if (!body) return;

    // Detect country prefix (+263 -> zw, +260 -> zm)
    let country = 'zm';
    if (sender.startsWith('263')) country = 'zw';
    if (body.toLowerCase().startsWith('!zw') || body.toLowerCase().startsWith('[zw]')) country = 'zw';
    if (body.toLowerCase().startsWith('!zm') || body.toLowerCase().startsWith('[zm]')) country = 'zm';

    console.log(`[Incoming WhatsApp] From: ${sender} | Country: ${country.toUpperCase()}`);
    console.log(`[Query]: "${body}"`);

    // Forward to Zedchatbot Backend
    const response = await fetch(`${BACKEND_URL}/chat`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        message: body,
        country: country,
        language: 'auto'
      })
    });

    if (!response.ok) {
      throw new Error(`Backend returned HTTP ${response.status}: ${response.statusText}`);
    }

    const data = await response.json();
    const rawAnswer = data.response || "I'm sorry, I couldn't find information on that.";

    const formattedAnswer = formatForWhatsApp(rawAnswer);
    const replyText = `${formattedAnswer}\n\n---\n*ZedChatBot | Community Assistant*`;

    // Reply directly to the sender on WhatsApp
    await message.reply(replyText);
    console.log(`[Sent Reply] Delivered answer (${formattedAnswer.length} chars) to ${sender}\n`);

  } catch (error) {
    console.error('[Bridge Error]:', error.message);
    try {
      await message.reply("Sorry, I encountered an internal error. Please try asking again in a moment.");
    } catch (sendErr) {
      console.error('[Send Error]:', sendErr.message);
    }
  }
});

// Start the client
client.initialize();
