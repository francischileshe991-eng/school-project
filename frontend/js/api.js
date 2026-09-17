const API_BASE = window.location.origin.includes(":8000") ? "" : "http://127.0.0.1:8000";

export async function sendMessageToAPI(text, country, language) {
  try {
    const response = await fetch(`${API_BASE}/chat`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        message: text,
        country: country,
        language: language,
      }),
    });

    if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
    }

    const data = await response.json();
    return data;
  } catch (error) {
    console.error("API Error:", error);
    return { 
        answer: "Error: Could not connect to the Zedchatbot backend server. Ensure it is running on port 8000.", 
        sources: [],
        interaction_id: null
    };
  }
}

export async function sendFeedbackToAPI(interactionId, rating, comment = "") {
  try {
    const response = await fetch(`${API_BASE}/feedback`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        interaction_id: interactionId,
        rating: rating,
        comment: comment,
      }),
    });

    if (!response.ok) {
      throw new Error(`Feedback error! status: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error("Feedback API Error:", error);
    return null;
  }
}
