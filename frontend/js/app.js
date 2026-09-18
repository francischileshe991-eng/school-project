import { sendMessageToAPI, sendFeedbackToAPI } from './api.js';
import { UI } from './ui.js';

const HISTORY_KEY = "zedchatbot-history";

function getGreeting(lang) {
  const greetings = {
    en: "Hello! I am Zedchatbot. How can I assist you with information about Zambia or Zimbabwe today?",
    bem: "Mwapoleni! Nine Zedchatbot. Kuti namwafwa shani ilelo?",
    ny: "Muli bwanji! Ine ndine Zedchatbot. Ndingakuyankheni bwanji lero?",
    sn: "Mhoro! Ini ndini Zedchatbot. Ndingakubatsirei sei nhasi?"
  };
  return greetings[lang] || greetings.en;
}

function loadHistory() {
  try {
    return JSON.parse(localStorage.getItem(HISTORY_KEY)) || [];
  } catch (_) {
    return [];
  }
}

function saveHistory() {
  try {
    localStorage.setItem(HISTORY_KEY, JSON.stringify(history));
  } catch (_) {
    // storage unavailable (private mode) — fail silently
  }
}

let history = loadHistory();

function renderHistory(handleFeedback) {
  const container = UI.messagesContainer;
  if (!container) return;

  history.forEach((entry) => {
    if (entry.role === "user") {
      UI.appendMessage(entry.text, "user");
    } else if (entry.role === "bot") {
      UI.appendMessage(entry.text, "bot", entry.sources || [], entry.interactionId || null, handleFeedback);
    } else if (entry.role === "error") {
      UI.appendMessage(entry.text, "error");
    }
  });
}

function init() {
  const form = document.getElementById("chat-form");
  const input = document.getElementById("message");
  const sendBtn = document.getElementById("send-btn");
  const currentCountry = document.getElementById("country");
  const currentLanguage = document.getElementById("language");
  const suggestions = document.querySelectorAll(".suggestion-chip");

  if (!form || !input || !currentLanguage) return;

  function setBusy(busy) {
    input.disabled = busy;
    if (sendBtn) sendBtn.disabled = busy;
  }

  async function handleFeedback(interactionId, rating) {
    if (!interactionId) return;
    await sendFeedbackToAPI(interactionId, rating);
  }

  if (history.length === 0) {
    UI.appendMessage(getGreeting(currentLanguage.value), "bot");
  } else {
    renderHistory(handleFeedback);
  }

  async function submit(text) {
    const trimmed = text.trim();
    if (!trimmed || input.disabled) return;

    UI.appendMessage(trimmed, "user");
    history.push({ role: "user", text: trimmed });
    saveHistory();
    input.value = "";

    UI.showTypingIndicator();
    setBusy(true);

    const country = currentCountry ? currentCountry.value : "zm";
    const language = currentLanguage.value;

    try {
      const response = await sendMessageToAPI(trimmed, country, language);

      if (response && response.error) {
        UI.removeTypingIndicator();
        UI.appendMessage(response.error, "error");
        history.push({ role: "error", text: response.error });
      } else if (response && response.answer) {
        UI.removeTypingIndicator();
        UI.appendMessage(
          response.answer,
          "bot",
          response.sources || [],
          response.interaction_id || null,
          handleFeedback
        );
        history.push({
          role: "bot",
          text: response.answer,
          sources: response.sources || [],
          interactionId: response.interaction_id || null,
        });
      } else {
        UI.removeTypingIndicator();
        UI.appendMessage("The assistant returned an empty response. Please try again.", "error");
        history.push({ role: "error", text: "The assistant returned an empty response. Please try again." });
      }
    } catch (error) {
      UI.removeTypingIndicator();
      UI.appendMessage(error.message || "Something went wrong. Please try again.", "error");
      history.push({ role: "error", text: error.message || "Something went wrong. Please try again." });
    } finally {
      setBusy(false);
      UI.scrollToBottom();
      input.focus();
    }

    saveHistory();
  }

  form.addEventListener("submit", (event) => {
    event.preventDefault();
    submit(input.value);
  });

  suggestions.forEach((chip) => {
    chip.addEventListener("click", () => {
      input.value = chip.dataset.prompt || "";
      submit(input.value);
    });
  });

  currentLanguage.addEventListener("change", () => {
    const container = UI.messagesContainer;
    if (container) container.innerHTML = "";
    history = [];
    saveHistory();
    UI.appendMessage(getGreeting(currentLanguage.value), "bot");
  });
}

if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", init);
} else {
  init();
}