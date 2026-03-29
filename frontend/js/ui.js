export const UI = {
  messagesContainer: document.getElementById("messages"),

  appendMessage(text, className) {
    const item = document.createElement("article");
    item.className = `message ${className}`;
    item.textContent = text;

    this.messagesContainer.appendChild(item);
    this.scrollToBottom();
  },

  showTypingIndicator() {
    const loader = document.createElement("div");
    loader.className = "message bot typing-indicator";
    loader.id = "typing-indicator";
    [".", ".", "."].forEach((dot) => {
      const span = document.createElement("span");
      span.textContent = dot;
      loader.appendChild(span);
    });
    this.messagesContainer.appendChild(loader);
    this.scrollToBottom();
  },

  removeTypingIndicator() {
    const loader = document.getElementById("typing-indicator");
    if (loader) {
      loader.remove();
    }
  },

  scrollToBottom() {
    // Smooth scroll to bottom
    setTimeout(() => {
        this.messagesContainer.scrollTo({
            top: this.messagesContainer.scrollHeight,
            behavior: 'smooth'
        });
    }, 10);
  }
};
