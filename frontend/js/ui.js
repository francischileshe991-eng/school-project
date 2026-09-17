export const UI = {
  get messagesContainer() {
    return document.getElementById("messages");
  },

  appendMessage(text, className, sources = [], interactionId = null, onFeedback = null) {
    const container = this.messagesContainer;
    if (!container) return;

    const item = document.createElement("article");
    item.className = `message ${className}`;

    const textContent = document.createElement("div");
    textContent.textContent = text;
    item.appendChild(textContent);

    // Display sources if available
    if (sources && sources.length > 0) {
      const sourcesBox = document.createElement("div");
      sourcesBox.className = "sources-box";
      const cleanedSources = sources.map(s => s.split(/[\\/]/).pop());
      sourcesBox.textContent = `Sources: ${cleanedSources.join(", ")}`;
      item.appendChild(sourcesBox);
    }

    // Display rating buttons if this is a bot message with an interaction ID
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
    loader.className = "message bot typing-indicator";
    loader.id = "typing-indicator";
    [".", ".", "."].forEach((dot) => {
      const span = document.createElement("span");
      span.textContent = dot;
      loader.appendChild(span);
    });
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
