function escapeHtml(str) {
  return String(str)
    .replace(/\uFFFD/g, "")
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#39;");
}

function safeUrl(url) {
  const trimmed = url.trim();
  return /^(https?:|mailto:)/i.test(trimmed) ? trimmed : "";
}

function renderInline(text) {
  let s = text;

  s = s.replace(/\[([^\]]+)\]\(([^)]+)\)/g, (match, label, url) => {
    const href = safeUrl(url);
    if (!href) return match;
    return `<a href="${href}" target="_blank" rel="noopener noreferrer">${label}</a>`;
  });

  s = s.replace(/`([^`]+)`/g, (match, code) => `<code>${code}</code>`);

  // Step highlight badge: converts "**Step 1...**" to a prominent, styled step badge
  s = s.replace(/\*\*(Step\s+\d+[^:*]*[:)]?)\*\*/gi, '<strong class="step-badge">$1</strong>');

  // Standard markdown bold
  s = s.replace(/\*\*([^*]+)\*\*/g, "<strong>$1</strong>");

  // Standard markdown italic
  s = s.replace(/(^|[^*\w])\*([^*\n]+?)\*(?=[^*\w]|$)/g, "$1<em>$2</em>");

  return s;
}

function renderMarkdown(md) {
  if (!md) return "";

  // 1. Clean and normalize line endings
  let normalized = escapeHtml(md).replace(/\r\n/g, "\n");

  // 2. Pre-process inline squashed bullets onto separate lines:
  normalized = normalized.replace(/([:.]|\b)\s+-\s+(\*\*|Step|[A-Z])/g, "$1\n- $2");

  const lines = normalized.split("\n");
  const out = [];
  let currentList = null;
  let para = [];

  function closeList() {
    if (currentList) {
      out.push(currentList === "ul" ? "</ul>" : "</ol>");
      currentList = null;
    }
  }

  function flushPara() {
    if (para.length) {
      out.push(`<p>${renderInline(para.join("<br>"))}</p>`);
      para = [];
    }
  }

  for (let i = 0; i < lines.length; i++) {
    const raw = lines[i];
    const line = raw.trim();

    if (!line) {
      flushPara();
      const nextRaw = i + 1 < lines.length ? lines[i + 1].trim() : "";
      const isNextList = /^[-*]\s+|^\d+\.\s+/.test(nextRaw);
      if (!isNextList) {
        closeList();
      }
      continue;
    }

    // Headings
    const heading = line.match(/^(#{1,4})\s+(.*)$/);
    if (heading) {
      flushPara();
      closeList();
      const level = heading[1].length;
      out.push(`<h${level}>${renderInline(heading[2])}</h${level}>`);
      continue;
    }

    // List items
    const isSubItem = /^(\s{2,}|\t)[-*]\s+/.test(raw);
    const bullet = line.match(/^[-*]\s+(.*)$/);
    const numbered = line.match(/^\d+\.\s+(.*)$/);

    if (bullet || numbered) {
      flushPara();
      const tag = bullet ? "ul" : "ol";

      if (currentList !== tag) {
        closeList();
        out.push(`<${tag}>`);
        currentList = tag;
      }

      const content = renderInline(bullet ? bullet[1] : numbered[1]);
      const subClass = isSubItem ? ' class="sub-item"' : "";
      out.push(`<li${subClass}>${content}</li>`);
      continue;
    }

    // Regular paragraph text
    if (currentList) closeList();
    para.push(line);
  }

  flushPara();
  closeList();
  return out.join("\n");
}

export const UI = {
  get messagesContainer() {
    return document.getElementById("messages");
  },

  setConversationMode(active) {
    const heroStage = document.getElementById("hero-stage");
    const conversationStage = document.getElementById("conversation-stage");
    if (active) {
      document.body.classList.add("in-conversation");
      if (heroStage) heroStage.style.display = "none";
      if (conversationStage) conversationStage.style.display = "block";
    } else {
      document.body.classList.remove("in-conversation");
      if (heroStage) heroStage.style.display = "flex";
      if (conversationStage) conversationStage.style.display = "none";
    }
  },

  appendMessage(text, role, sources = [], interactionId = null, onFeedback = null, lang = null, onRetry = null) {
    const container = this.messagesContainer;
    if (!container) return;

    // Activate conversation mode
    this.setConversationMode(true);

    const row = document.createElement("div");
    row.className = `message-row ${role}`;

    if (role === "user") {
      const bubble = document.createElement("div");
      bubble.className = "message-bubble-user";
      bubble.textContent = text;
      row.appendChild(bubble);
    } else if (role === "bot") {
      const card = document.createElement("article");
      card.className = "message-card-bot";
      card.setAttribute("role", "status");
      if (lang) card.setAttribute("lang", lang);

      // Bot Card Header with Mini Avatar
      const header = document.createElement("div");
      header.className = "bot-card-header";
      header.innerHTML = `
        <div class="bot-card-brand">
          <img src="./assets/images/logo.jpeg" alt="ZedChatBot" class="bot-mini-avatar" />
          <span class="bot-brand-label">ZedChatBot AI</span>
          <span class="bot-verified-badge">✓ Grounded</span>
        </div>
      `;

      // Copy Response Button
      const copyBtn = document.createElement("button");
      copyBtn.className = "copy-btn";
      copyBtn.innerHTML = `
        <svg viewBox="0 0 24 24" width="13" height="13" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <rect x="9" y="9" width="13" height="13" rx="2" ry="2"/>
          <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/>
        </svg>
        <span>Copy</span>
      `;
      copyBtn.addEventListener("click", async () => {
        try {
          await navigator.clipboard.writeText(text);
          copyBtn.innerHTML = `<span>✓ Copied</span>`;
          setTimeout(() => {
            copyBtn.innerHTML = `
              <svg viewBox="0 0 24 24" width="13" height="13" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <rect x="9" y="9" width="13" height="13" rx="2" ry="2"/>
                <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/>
              </svg>
              <span>Copy</span>
            `;
          }, 2000);
        } catch (_) {}
      });
      header.appendChild(copyBtn);
      card.appendChild(header);

      // Bot Body Content
      const body = document.createElement("div");
      body.className = "bot-body";
      body.innerHTML = renderMarkdown(text);
      card.appendChild(body);

      // Verified Sources Box
      if (sources && sources.length > 0) {
        const sourcesBox = document.createElement("div");
        sourcesBox.className = "sources-box";
        sourcesBox.innerHTML = `<div class="sources-label">Official Sources Citations</div>`;

        const tagsContainer = document.createElement("div");
        tagsContainer.className = "sources-tags";
        sources.forEach((src) => {
          const tag = document.createElement("span");
          tag.className = "source-tag";
          tag.textContent = String(src).split(/[\\/]/).pop();
          tagsContainer.appendChild(tag);
        });
        sourcesBox.appendChild(tagsContainer);
        card.appendChild(sourcesBox);
      }

      // Card Footer with TAM Feedback (Helpful? Yes / No)
      if (interactionId && onFeedback) {
        const footer = document.createElement("div");
        footer.className = "bot-card-footer";
        footer.innerHTML = `
          <div class="feedback-controls">
            <span style="font-size: 0.775rem; color: var(--text-muted); font-weight: 500; margin-right: 0.25rem;">Accurate?</span>
          </div>
        `;

        const thumbsUp = document.createElement("button");
        thumbsUp.className = "feedback-btn";
        thumbsUp.textContent = "👍 Yes";
        thumbsUp.title = "Accurate & grounded (5 stars)";

        const thumbsDown = document.createElement("button");
        thumbsDown.className = "feedback-btn";
        thumbsDown.textContent = "👎 Inaccurate";
        thumbsDown.title = "Inaccurate or incomplete (1 star)";

        thumbsUp.addEventListener("click", async () => {
          thumbsUp.disabled = true;
          thumbsDown.disabled = true;
          thumbsUp.classList.add("active");
          await onFeedback(interactionId, 5);
          footer.querySelector(".feedback-controls").innerHTML = `<span class="feedback-thanks">✓ Thank you for validating!</span>`;
        });

        thumbsDown.addEventListener("click", async () => {
          thumbsUp.disabled = true;
          thumbsDown.disabled = true;
          thumbsDown.classList.add("active");
          await onFeedback(interactionId, 1);
          footer.querySelector(".feedback-controls").innerHTML = `<span class="feedback-thanks">✓ Feedback recorded for research evaluation.</span>`;
        });

        footer.querySelector(".feedback-controls").appendChild(thumbsUp);
        footer.querySelector(".feedback-controls").appendChild(thumbsDown);
        card.appendChild(footer);
      }

      row.appendChild(card);
    } else if (role === "error") {
      const errCard = document.createElement("div");
      errCard.className = "message-card-error";

      const errText = document.createElement("span");
      errText.className = "error-text";
      errText.textContent = text;
      errCard.appendChild(errText);

      if (onRetry) {
        const retryBtn = document.createElement("button");
        retryBtn.type = "button";
        retryBtn.className = "error-retry-btn";
        retryBtn.innerHTML = `
          <svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <polyline points="23 4 23 10 17 10"></polyline>
            <path d="M20.49 15a9 9 0 1 1-2.12-9.36L23 10"></path>
          </svg>
          <span>Try again</span>
        `;
        retryBtn.addEventListener("click", () => {
          retryBtn.disabled = true;
          onRetry();
        });
        errCard.appendChild(retryBtn);
      }

      row.appendChild(errCard);
    }

    container.appendChild(row);
    this.scrollToBottom();
  },

  showTypingIndicator() {
    const container = this.messagesContainer;
    if (!container) return;

    this.setConversationMode(true);

    const loaderRow = document.createElement("div");
    loaderRow.className = "message-row bot";
    loaderRow.id = "typing-row";

    const indicator = document.createElement("div");
    indicator.className = "typing-indicator";
    indicator.id = "typing-indicator";
    indicator.setAttribute("role", "status");
    indicator.setAttribute("aria-label", "ZedChatBot is retrieving and reasoning");

    for (let i = 0; i < 3; i++) {
      const dot = document.createElement("span");
      dot.setAttribute("aria-hidden", "true");
      indicator.appendChild(dot);
    }

    loaderRow.appendChild(indicator);
    container.appendChild(loaderRow);
    this.scrollToBottom();
  },

  removeTypingIndicator() {
    const row = document.getElementById("typing-row");
    if (row) row.remove();
    const loader = document.getElementById("typing-indicator");
    if (loader) loader.remove();
  },

  scrollToBottom() {
    setTimeout(() => {
      window.scrollTo({
        top: document.body.scrollHeight,
        behavior: 'smooth'
      });
    }, 15);
  }
};