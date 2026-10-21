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
    en: "Hello! I am Zedchatbot. Ask me about public records, education, utilities, health, agriculture or community funding today?",
    bem: "Mwapoleni! Nine Zedchatbot. Kuti namwafwa pa fya boma, amasambililo, amenshi ne amagetsi, ubumi, ubulimi nangu CDF?",
    ny: "Muli bwanji! Ine ndine Zedchatbot. Ndingakuyankheni bwanji pa za boma, maphunziro, madzi ndi magetsi, zaumoyo, ulimi kapena CDF?",
    sn: "Mhoro! Ini ndini Zedchatbot. Ndingakubatsirei sei nezve mabasa ehurumende, dzidzo, mvura nemagetsi, hutano, kurima kana CDF?"
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

const ICONS = {
  bolt: '<polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"></polygon>',
  card: '<rect x="3" y="4" width="18" height="16" rx="2"></rect><line x1="7" y1="8" x2="11" y2="8"></line><line x1="7" y1="12" x2="17" y2="12"></line><line x1="7" y1="16" x2="13" y2="16"></line>',
  cap: '<path d="M22 10v6M2 10l10-5 10 5-10 5z"></path><path d="M6 12v5c3 3 9 3 12 0v-5"></path>',
  shield: '<path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"></path><line x1="12" y1="8" x2="12" y2="14"></line><line x1="9" y1="11" x2="15" y2="11"></line>',
  plant: '<path d="M7 20h10"></path><path d="M10 20c0-4.4 2-7.8 6-9"></path><path d="M16 11c-2-4-6-4-8-1-2 3-1 6 2 8"></path><path d="M12 20V4"></path>',
  bank: '<line x1="3" y1="21" x2="21" y2="21"></line><line x1="6" y1="18" x2="6" y2="11"></line><line x1="10" y1="18" x2="10" y2="11"></line><line x1="14" y1="18" x2="14" y2="11"></line><line x1="18" y1="18" x2="18" y2="11"></line><polygon points="12 2 20 7 4 7 12 2"></polygon>',
  percent: '<line x1="19" y1="5" x2="5" y2="19"></line><circle cx="6.5" cy="6.5" r="2.5"></circle><circle cx="17.5" cy="17.5" r="2.5"></circle>',
  passport: '<rect x="5" y="3" width="14" height="18" rx="2"></rect><circle cx="12" cy="10" r="3"></circle><line x1="8.5" y1="17" x2="15.5" y2="17"></line>',
  doc: '<path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path><polyline points="14 2 14 8 20 8"></polyline><line x1="8" y1="13" x2="16" y2="13"></line><line x1="8" y1="17" x2="13" y2="17"></line>'
};

const SUGGESTIONS = {
  en: {
    zm: [
      { label: "2026 ZESCO Tariffs", icon: "bolt", prompt: "What are the 2026 ZESCO electricity tariffs?" },
      { label: "Green NRC Card", icon: "card", prompt: "How do I apply for a National Registration Card (NRC)?" },
      { label: "UNZA Admission", icon: "cap", prompt: "What are the requirements for applying to UNZA?" },
      { label: "NHIMA Insurance", icon: "shield", prompt: "How do I contribute to NHIMA health insurance?" },
      { label: "FISP Agriculture", icon: "plant", prompt: "How do farmers apply for FISP fertilizer and seed?" },
      { label: "How do I get or apply for CDF?", icon: "bank", prompt: "How do I get or apply for CDF?" }
    ],
    zw: [
      { label: "ZIMSEC Results", icon: "doc", prompt: "How do I check my ZIMSEC results online?" },
      { label: "Zimbabwe ID", icon: "card", prompt: "How do I apply for a Zimbabwe National Identity Card (ID)?" },
      { label: "e-Passport", icon: "passport", prompt: "What are the requirements and fees for the Zimbabwe e-passport?" },
      { label: "UZ Admission", icon: "cap", prompt: "What are the requirements for University of Zimbabwe (UZ) admission?" },
      { label: "ZIMRA Tax", icon: "percent", prompt: "What are the 2024 ZIMRA PAYE tax thresholds and Aids Levy?" },
      { label: "Health Guidance", icon: "shield", prompt: "How can I prevent cholera and malaria in Zimbabwe?" }
    ]
  },
  bem: [
    { label: "Kuti napoka shani NRC?", icon: "card", prompt: "Kuti napoka shani NRC mu Zambia?" },
    { label: "Ama tariffs ya ZESCO 2026?", icon: "bolt", prompt: "Ama tariffs ya ZESCO ya malaiti yaba shani muli 2026?" },
    { label: "Kuti napempula shani CDF?", icon: "bank", prompt: "Kuti napempula shani indalama sha CDF ku ward yandi?" },
    { label: "Finshi balefwaya pa UNZA?", icon: "cap", prompt: "Finshi balefwaya pa kuti banjelele pa UNZA nangu CBU?" },
    { label: "Kuti nailemba shani NHIMA?", icon: "shield", prompt: "Kuti nailemba shani kuli NHIMA pa kuti ing'anda yandi ifwalwe ubumi?" },
    { label: "Abalimi bapoka shani FISP?", icon: "plant", prompt: "Abalimi bapoka shani umufundo wa FISP no mbuto muli uno mwaka?" }
  ],
  ny: [
    { label: "Ndingatenge bwanji NRC?", icon: "card", prompt: "Kodi ndingatenge bwanji NRC yatsopano mu Zambia?" },
    { label: "Ndingapemphe bwanji HELSB?", icon: "cap", prompt: "Ndingapemphe bwanji ngongole ya maphunziro ku HELSB?" },
    { label: "Ndingapeze bwanji TPIN?", icon: "percent", prompt: "Ndingapeze bwanji TPIN kuchokera ku ZRA pa internet?" },
    { label: "Ndingalipire bwanji madzi a LWSC?", icon: "doc", prompt: "Ndingalipire bwanji ma bill a madzi a LWSC ku Lusaka?" },
    { label: "Katemera wa mwana?", icon: "shield", prompt: "Ndi katemera wanji wofunikira pa Under-5 clinic ya mwana?" },
    { label: "Provisional license ya RTSA?", icon: "passport", prompt: "Ndingatenge bwanji provisional driver's license ku RTSA?" }
  ],
  sn: [
    { label: "Ndingawana sei chitupa?", icon: "card", prompt: "Ndingawana sei chitupa chekuzvarwa muZimbabwe?" },
    { label: "Passport yeZimbabwe?", icon: "passport", prompt: "Ndinganyorera sei passport yeZimbabwe uye inodhura marii?" },
    { label: "ZIMSEC results?", icon: "doc", prompt: "Ndingaona sei mibairo yeZIMSEC pamhepo?" },
    { label: "ZIMRA tax 2024?", icon: "percent", prompt: "Ndeapi mitero yeZIMRA PAYE ya2024?" },
    { label: "UZ admission?", icon: "cap", prompt: "Ndezvipi zvinodiwa kuti ndipinde paYunivhesiti yeZimbabwe?" },
    { label: "Kudzivirira kolera?", icon: "shield", prompt: "Ndingadzivirire sei kolera nemalarari muZimbabwe?" }
  ]
};

function getSuggestionItems(country, lang) {
  if (lang === "en") {
    const enSet = SUGGESTIONS.en || {};
    return enSet[country] || enSet.zm || [];
  }
  return SUGGESTIONS[lang] || (SUGGESTIONS.en && SUGGESTIONS.en[country]) || [];
}

function escapeAttr(value) {
  return String(value)
    .replace(/&/g, "&amp;")
    .replace(/"/g, "&quot;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;");
}

function init() {
  const form = document.getElementById("chat-form");
  const input = document.getElementById("message");
  const sendBtn = document.getElementById("send-btn");
  const currentCountry = document.getElementById("country");
  const currentLanguageSelect = document.getElementById("language");
  const suggestionsGrid = document.getElementById("suggestions-grid");
  const newChatBtn = document.getElementById("new-chat-btn");
  const themeToggleBtn = document.getElementById("theme-toggle-btn");
  const brandHome = document.getElementById("brand-home");


  if (!form || !input) return;

  // Auto-hide the top nav while scrolling down (reading), reveal it on scroll up
  const topNav = document.querySelector(".top-nav");
  if (topNav) {
    let lastScrollY = window.scrollY;
    let navTicking = false;
    const updateNav = () => {
      const y = window.scrollY;
      if (y <= 60 || y < lastScrollY - 4) {
        topNav.classList.remove("nav-hidden");
      } else if (y > lastScrollY + 4) {
        topNav.classList.add("nav-hidden");
      }
      lastScrollY = y;
      navTicking = false;
    };
    window.addEventListener("scroll", () => {
      if (!navTicking) {
        window.requestAnimationFrame(updateNav);
        navTicking = true;
      }
    }, { passive: true });
  }

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
        UI.appendMessage(entry.text, "bot", entry.sources || [], entry.interactionId || null, handleFeedback, entry.lang);
      } else if (entry.role === "error") {
        const retryFn = entry.prompt ? () => runQuery(entry.prompt, false) : null;
        UI.appendMessage(entry.text, "error", [], null, null, null, retryFn);
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
    if (topNav) topNav.classList.remove("nav-hidden");
    input.value = "";
    input.style.height = "auto";
    input.focus();
  }

  if (newChatBtn) newChatBtn.addEventListener("click", resetConversation);
  if (brandHome) brandHome.addEventListener("click", (e) => {
    e.preventDefault();
    resetConversation();
  });

  async function runQuery(trimmed, echoUser) {
    if (!trimmed || input.disabled) return;

    const country = currentCountry ? currentCountry.value : "zm";
    const language = currentLanguageSelect ? currentLanguageSelect.value : "en";
    const retry = () => runQuery(trimmed, false);

    UI.setConversationMode(true);

    if (echoUser) {
      UI.appendMessage(trimmed, "user");
      history.push({ role: "user", text: trimmed });
      saveHistory(history);
      input.value = "";
      input.style.height = "auto";
    }

    UI.showTypingIndicator();
    setBusy(true);

    try {
      const response = await sendMessageToAPI(trimmed, country, language);

      if (response && response.error) {
        UI.removeTypingIndicator();
        UI.appendMessage(response.error, "error", [], null, null, null, retry);
        history.push({ role: "error", text: response.error, prompt: trimmed });
      } else if (response && (response.answer || response.response)) {
        UI.removeTypingIndicator();
        const answerText = response.answer || response.response;
        UI.appendMessage(
          answerText,
          "bot",
          response.sources || [],
          response.interaction_id || null,
          handleFeedback,
          language
        );
        history.push({
          role: "bot",
          text: answerText,
          sources: response.sources || [],
          interactionId: response.interaction_id || null,
          lang: language,
        });
      } else {
        UI.removeTypingIndicator();
        const emptyMsg = "The assistant returned an empty response. Please try again.";
        UI.appendMessage(emptyMsg, "error", [], null, null, null, retry);
        history.push({ role: "error", text: emptyMsg, prompt: trimmed });
      }
    } catch (error) {
      UI.removeTypingIndicator();
      const errMsg = error.message || "Something went wrong. Please try again.";
      UI.appendMessage(errMsg, "error", [], null, null, null, retry);
      history.push({ role: "error", text: errMsg, prompt: trimmed });
    } finally {
      setBusy(false);
      UI.scrollToBottom();
      input.focus();
      saveHistory(history);
    }
  }

  async function submit(text) {
    const trimmed = text.trim();
    if (!trimmed || input.disabled) return;
    return runQuery(trimmed, true);
  }

  form.addEventListener("submit", (event) => {
    event.preventDefault();
    submit(input.value);
  });

  function renderSuggestions() {
    if (!suggestionsGrid) return;
    const country = currentCountry ? currentCountry.value : "zm";
    const lang = currentLanguageSelect ? currentLanguageSelect.value : "en";
    const items = getSuggestionItems(country, lang);
    suggestionsGrid.innerHTML = items
      .map(
        (item) => `
        <button type="button" class="suggestion-chip" data-prompt="${escapeAttr(item.prompt)}">
          <span class="chip-svg-wrap">
            <svg viewBox="0 0 24 24" width="15" height="15" fill="none" stroke="currentColor" stroke-width="2"
              stroke-linecap="round" stroke-linejoin="round">${ICONS[item.icon] || ""}</svg>
          </span>
          <span>${escapeAttr(item.label)}</span>
        </button>`
      )
      .join("");
  }

  renderSuggestions();

  if (currentCountry) {
    currentCountry.addEventListener("change", renderSuggestions);
  }

  if (currentLanguageSelect) {
    currentLanguageSelect.addEventListener("change", renderSuggestions);
  }

  if (suggestionsGrid) {
    suggestionsGrid.addEventListener("click", (event) => {
      const chip = event.target.closest(".suggestion-chip");
      if (!chip) return;
      const promptText = chip.dataset.prompt || "";
      if (promptText) {
        input.value = promptText;
        submit(promptText);
      }
    });
  }
}

if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", init);
} else {
  init();
}