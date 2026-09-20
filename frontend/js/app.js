import { sendMessageToAPI, sendFeedbackToAPI } from './api.js';
import { UI } from './ui.js';

const HISTORY_KEY = "zedchatbot-history";
const THEME_KEY = "zedchatbot-theme";

function applyTheme(theme) {
  document.documentElement.setAttribute("data-theme", theme);
  try {
    localStorage.setItem(THEME_KEY, theme);
  } catch (_) {}
}

function initTheme() {
  try {
    const saved = localStorage.getItem(THEME_KEY);
    if (saved) {
      applyTheme(saved);
    } else {
      const prefersDark = window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches;
      applyTheme(prefersDark ? "dark" : "light");
    }
  } catch (_) {
    applyTheme("light");
  }
}

// Immediately initialize theme before DOMContentLoaded to avoid theme flashing
initTheme();

function getGreeting(lang) {
  const greetings = {
    en: "Hello! I am Zedchatbot. How can I assist you with public records, education, or utilities today?",
    bem: "Mwapoleni! Nine Zedchatbot. Kuti namwafwa shani pa fya boma, amagetsi, nangu ama applications ilelo?",
    ny: "Muli bwanji! Ine ndine Zedchatbot. Ndingakuyankheni bwanji pa za boma, magetsi kapena maphunziro lero?",
    sn: "Mhoro! Ini ndini Zedchatbot. Ndingakubatsirei sei nezve mabasa ehurumende kana dzidzo nhasi?"
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

function saveHistory(history) {
  try {
    localStorage.setItem(HISTORY_KEY, JSON.stringify(history));
  } catch (_) {}
}

let history = loadHistory();

function init() {
  const form = document.getElementById("chat-form");
  const input = document.getElementById("message");
  const sendBtn = document.getElementById("send-btn");
  const currentCountry = document.getElementById("country");
  const currentLanguageSelect = document.getElementById("language");
  const suggestions = document.querySelectorAll(".suggestion-chip");
  const newChatBtn = document.getElementById("new-chat-btn");
  const themeToggleBtn = document.getElementById("theme-toggle-btn");
  const brandHome = document.getElementById("brand-home");
  const sampleAskBtn = document.getElementById("btn-sample-ask");

  if (!form || !input) return;

  // Theme toggle listener
  if (themeToggleBtn) {
    themeToggleBtn.addEventListener("click", () => {
      const currentTheme = document.documentElement.getAttribute("data-theme") || "light";
      const nextTheme = currentTheme === "dark" ? "light" : "dark";
      applyTheme(nextTheme);
    });
  }


  function setBusy(busy) {
    input.disabled = busy;
    if (sendBtn) sendBtn.disabled = busy;
  }

  async function handleFeedback(interactionId, rating) {
    if (!interactionId) return;
    await sendFeedbackToAPI(interactionId, rating);
  }


  // Auto-resize textarea as user types
  function adjustTextareaHeight() {
    input.style.height = "auto";
    const newHeight = Math.min(input.scrollHeight, 180);
    input.style.height = `${newHeight}px`;
  }
  input.addEventListener("input", adjustTextareaHeight);

  // Submit on Enter key (without Shift)
  input.addEventListener("keydown", (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      form.requestSubmit();
    }
  });

  // Render previous history if any exists
  if (history.length > 0) {
    UI.setConversationMode(true);
    history.forEach((entry) => {
      if (entry.role === "user") {
        UI.appendMessage(entry.text, "user");
      } else if (entry.role === "bot") {
        UI.appendMessage(entry.text, "bot", entry.sources || [], entry.interactionId || null, handleFeedback);
      } else if (entry.role === "error") {
        UI.appendMessage(entry.text, "error");
      }
    });
  } else {
    UI.setConversationMode(false);
  }

  // Reset to new conversation
  function resetConversation() {
    history = [];
    saveHistory(history);
    const container = UI.messagesContainer;
    if (container) container.innerHTML = "";
    UI.setConversationMode(false);
    input.value = "";
    input.style.height = "auto";
    input.focus();
  }

  if (newChatBtn) newChatBtn.addEventListener("click", resetConversation);
  if (brandHome) brandHome.addEventListener("click", (e) => {
    e.preventDefault();
    resetConversation();
  });

  // Sample prompt button
  if (sampleAskBtn) {
    sampleAskBtn.addEventListener("click", () => {
      input.value = "How do I apply for a National Registration Card (NRC)?";
      submit(input.value);
    });
  }

  async function submit(text) {
    const trimmed = text.trim();
    if (!trimmed || input.disabled) return;

    // Show conversation stage
    UI.setConversationMode(true);
    UI.appendMessage(trimmed, "user");
    history.push({ role: "user", text: trimmed });
    saveHistory(history);

    input.value = "";
    input.style.height = "auto";

    UI.showTypingIndicator();
    setBusy(true);

    const country = currentCountry ? currentCountry.value : "zm";
    const language = currentLanguageSelect ? currentLanguageSelect.value : "en";

    try {
      const response = await sendMessageToAPI(trimmed, country, language);

      if (response && response.error) {
        UI.removeTypingIndicator();
        UI.appendMessage(response.error, "error");
        history.push({ role: "error", text: response.error });
      } else if (response && (response.answer || response.response)) {
        UI.removeTypingIndicator();
        const answerText = response.answer || response.response;
        UI.appendMessage(
          answerText,
          "bot",
          response.sources || [],
          response.interaction_id || null,
          handleFeedback
        );
        history.push({
          role: "bot",
          text: answerText,
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
      saveHistory(history);
    }
  }

  form.addEventListener("submit", (event) => {
    event.preventDefault();
    submit(input.value);
  });

  suggestions.forEach((chip) => {
    chip.addEventListener("click", () => {
      const promptText = chip.dataset.prompt || "";
      if (promptText) {
        input.value = promptText;
        submit(promptText);
      }
    });
  });
}

if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", init);
} else {
  init();
}