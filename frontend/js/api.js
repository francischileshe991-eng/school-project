const API_BASE = "";
const REQUEST_TIMEOUT_MS = 200000; // 200s: accommodates local Ollama fallback generation time

async function postJSON(path, body, timeoutMs = REQUEST_TIMEOUT_MS) {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), timeoutMs);

  try {
    const response = await fetch(`${API_BASE}${path}`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(body),
      signal: controller.signal,
    });

    if (!response.ok) {
      let detail = `HTTP error! status: ${response.status}`;
      try {
        const err = await response.json();
        if (err && err.detail) {
          detail = typeof err.detail === "string" ? err.detail : JSON.stringify(err.detail);
        }
      } catch (_) {
        // ignore body parse failure
      }
      throw new Error(detail);
    }

    return await response.json();
  } catch (error) {
    if (error.name === "AbortError") {
      throw new Error("The request took too long and was cancelled. Please try again.");
    }
    throw error;
  } finally {
    clearTimeout(timer);
  }
}

export async function sendMessageToAPI(text, country, language) {
  try {
    return await postJSON("/chat", {
      message: text,
      country: country,
      language: language,
    });
  } catch (error) {
    console.error("API Error:", error);
    return {
      error: "Could not reach the Zedchatbot server. Ensure the backend is running, then try again.",
      sources: [],
      interaction_id: null,
    };
  }
}

export async function sendFeedbackToAPI(interactionId, rating, comment = "") {
  try {
    return await postJSON("/feedback", {
      interaction_id: interactionId,
      rating: rating,
      comment: comment,
    }, 15000);
  } catch (error) {
    console.error("Feedback API Error:", error);
    return null;
  }
}