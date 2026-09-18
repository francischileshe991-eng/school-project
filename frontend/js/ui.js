function escapeHtml(str) {
  return String(str)
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

  s = s.replace(/\*\*([^*]+)\*\*/g, "<strong>$1</strong>");

  s = s.replace(/(^|[^*\w])\*([^*\n]+?)\*(?=[^*\w]|$)/g, "$1<em>$2</em>");

  return s;
}

function renderMarkdown(md) {
  const escaped = escapeHtml(md).replace(/\r\n/g, "\n");
  const lines = escaped.split("\n");
  const out = [];
  let list = null;
  let para = [];

  function closeList() {
    if (list) {
      out.push(list === "ul" ? "</ul>" : "</ol>");
      list = null;
    }
  }

  function flushPara() {
    if (para.length) {
      out.push(`<p>${renderInline(para.join("<br>"))}</p>`);
      para = [];
    }
  }

  for (const raw of lines) {
    const line = raw.trim();
    if (!line) {
      flushPara();
      closeList();
      continue;
    }

    const heading = line.match(/^(#{1,4})\s+(.*)$/);
    if (heading) {
      flushPara();
      closeList();
      const level = heading[1].length;
      out.push(`<h${level}>${renderInline(heading[2])}</h${level}>`);
      continue;
    }

    const bullet = line.match(/^[-*]\s+(.*)$/);
    const numbered = line.match(/^\d+\.\s+(.*)$/);
    if (bullet || numbered) {
      flushPara();
      const tag = bullet ? "ul" : "ol";
      if (list !== tag) {
        closeList();
        out.push(`<${tag}>`);
        list = tag;
      }
      out.push(`<li>${renderInline((bullet ? bullet[1] : numbered[1]))}</li>`);
      continue;
    }

    if (list) closeList();
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

  appendMessage(text, className, sources = [], interactionId = null, onFeedback = null) {
    const container = this.messagesContainer;
    if (!container) return;

    const item = document.createElement("article");
    item.className = `message ${className}`;
    if (className === "bot" || className === "error") {
      item.setAttribute("role", "status");
    }

    const textContent = document.createElement("div");
    const isMarkup = className === "bot";
    textContent.innerHTML = isMarkup ? renderMarkdown(text) : escapeHtml(text);
    item.appendChild(textContent);

    if (sources && sources.length > 0) {
      const sourcesBox = document.createElement("div");
      sourcesBox.className = "sources-box";
      sourcesBox.setAttribute("aria-label", "Sources");

      const label = document.createElement("span");
      label.className = "sources-label";
      label.textContent = "Sources";
      sourcesBox.appendChild(label);

      const list = document.createElement("ul");
      list.className = "sources-list";
      sources.forEach((src) => {
        const li = document.createElement("li");
        const chip = document.createElement("span");
        chip.className = "source-chip";
        chip.textContent = String(src).split(/[\\/]/).pop();
        li.appendChild(chip);
        list.appendChild(li);
      });
      sourcesBox.appendChild(list);
      item.appendChild(sourcesBox);
    }

    if (className === "bot" && interactionId && onFeedback) {
      const feedbackBar = document.createElement("div");
      feedbackBar.className = "feedback-bar";
      feedbackBar.innerHTML = `<span>Helpful?</span>`;

      const thumbsUp = document.createElement("button");
      thumbsUp.className = "feedback-btn";
      thumbsUp.textContent = "👍 Yes";
      thumbsUp.title = "Mark as accurate/helpful (5 stars)";

      const thumbsDown = document.createElement("button");
      thumbsDown.className = "feedback-btn";
      thumbsDown.textContent = "👎 No";
      thumbsDown.title = "Mark as inaccurate (1 star)";

      thumbsUp.addEventListener("click", async () => {
        thumbsUp.disabled = true;
        thumbsDown.disabled = true;
        thumbsUp.classList.add("active");
        await onFeedback(interactionId, 5);
        feedbackBar.innerHTML = `<span class="feedback-thanks">✓ Thank you for your feedback!</span>`;
      });

      thumbsDown.addEventListener("click", async () => {
        thumbsUp.disabled = true;
        thumbsDown.disabled = true;
        thumbsDown.classList.add("active");
        await onFeedback(interactionId, 1);
        feedbackBar.innerHTML = `<span class="feedback-thanks">✓ Feedback noted, thank you!</span>`;
      });

      feedbackBar.appendChild(thumbsUp);
      feedbackBar.appendChild(thumbsDown);
      item.appendChild(feedbackBar);
    }

    container.appendChild(item);
    this.scrollToBottom();
  },

  showTypingIndicator() {
    const container = this.messagesContainer;
    if (!container) return;

    const loader = document.createElement("div");
    loader.className = "typing-indicator";
    loader.id = "typing-indicator";
    loader.setAttribute("role", "status");
    loader.setAttribute("aria-label", "Zedchatbot is thinking");
    for (let i = 0; i < 3; i++) {
      const span = document.createElement("span");
      span.setAttribute("aria-hidden", "true");
      loader.appendChild(span);
    }
    container.appendChild(loader);
    this.scrollToBottom();
  },

  removeTypingIndicator() {
    const loader = document.getElementById("typing-indicator");
    if (loader) {
      loader.remove();
    }
  },

  scrollToBottom() {
    const container = this.messagesContainer;
    if (!container) return;

    setTimeout(() => {
      container.scrollTo({
        top: container.scrollHeight,
        behavior: 'smooth'
      });
    }, 10);
  }
};