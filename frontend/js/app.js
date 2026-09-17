import { sendMessageToAPI, sendFeedbackToAPI } from './api.js';
import { UI } from './ui.js';

function init() {
  const form = document.getElementById("chat-form");
  const input = document.getElementById("message");
  const currentCountry = document.getElementById("country");
  const currentLanguage = document.getElementById("language");

  if (!form || !input || !currentLanguage) return;

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

  // Initial greeting
  showGreeting();

  // Feedback handler callback
  async function handleFeedback(interactionId, rating) {
    if (!interactionId) return;
    await sendFeedbackToAPI(interactionId, rating);
  }

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
    const country = currentCountry ? currentCountry.value : "zm";
    const language = currentLanguage.value;
    const response = await sendMessageToAPI(text, country, language);
    
    // 4. Resolve UI State with Sources & Interactive Feedback
    UI.removeTypingIndicator();
    UI.appendMessage(
      response.answer,
      "bot",
      response.sources || [],
      response.interaction_id || null,
      handleFeedback
    );
    
    // 5. Scroll to bottom
    UI.scrollToBottom();
  });

  // Update greeting on language change
  currentLanguage.addEventListener("change", () => {
    const container = UI.messagesContainer;
    if (container) {
      container.innerHTML = "";
    }
    showGreeting();
  });
}

if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", init);
} else {
  init();
}
