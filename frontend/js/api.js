export async function sendMessageToAPI(text, country, language) {
  try {
    const response = await fetch("http://127.0.0.1:8000/chat", {
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
        answer: "Error: Could not connect to the Zedchatbot backend server. Ensure it is running.", 
        sources: [] 
    };
  }
}
