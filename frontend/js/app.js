import { sendMessageToAPI } from './api.js';
import { UI } from './ui.js';

const form = document.getElementById("chat-form");
const input = document.getElementById("message");
const currentCountry = document.getElementById("country");
const currentLanguage = document.getElementById("language");

// Initial Greeting
function showGreeting() {
  const lang = currentLanguage.value;
  const greetings = {
    en: "Hello! I am Zedchatbot. How can I assist you with information about Zambia or Zimbabwe today?",
    bem: "Mwapoleni! Nine Zedchatbot. Kuti namwafwa shani ilelo?",
    ny: "Muli bwanji! Ine ndine Zedchatbot. Ndingakuyankheni bwanji lero?",
    sn: "Mhoro! Ini ndini Zedchatbot. Ndingakubatsirei sei nhasi?"
  };
  UI.appendMessage(greetings[lang] || greetings.en, "bot");
}

// Handle Startup
window.addEventListener("DOMContentLoaded", showGreeting);

// Handle Chat Submission
form.addEventListener("submit", async (event) => {
  event.preventDefault();

  const text = input.value.trim();
  if (!text) return;

  // 1. Render User Message
  UI.appendMessage(text, "user");
  input.value = "";
  
  // 2. Show UI Loading State
  UI.showTypingIndicator();

  // 3. Send Network Call to Backend
  const country = currentCountry.value;
  const language = currentLanguage.value;
  const response = await sendMessageToAPI(text, country, language);
  
  // 4. Resolve UI State
  UI.removeTypingIndicator();
  UI.appendMessage(response.answer, "bot");
  
  // 5. Scroll to bottom just in case
  UI.scrollToBottom();
});

// Update greeting on language change
currentLanguage.addEventListener("change", () => {
  UI.messagesContainer.innerHTML = "";
  showGreeting();
});

