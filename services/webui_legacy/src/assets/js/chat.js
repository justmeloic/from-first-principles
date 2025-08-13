document.addEventListener("DOMContentLoaded", () => {
    const chatMessages = document.getElementById("chat-messages");
    const chatInput = document.getElementById("chat-input");
    const sendBtn = document.getElementById("send-btn");
    const aiFunctionalitySelect = document.getElementById("ai-functionality-select");

    // Generate a unique session ID for the user (using localStorage)
    let sessionId = localStorage.getItem("session_id");
    if (!sessionId) {
      sessionId = generateSessionId();
      localStorage.setItem("session_id", sessionId);
    }

    const addMessage = (text, sender) => {
      const messageDiv = document.createElement("div");
      messageDiv.className = `message ${sender}`;

      if (sender === "bot") {
        const img = document.createElement("img");
        img.src = "../assets/images/tab-logo.png"; // Update with your bot's image path
        img.alt = "Bot Logo";
        messageDiv.appendChild(img);
      }

      messageDiv.append(text);
      chatMessages.appendChild(messageDiv);
      chatMessages.scrollTop = chatMessages.scrollHeight;
    };

    const sendMessage = async () => {
      const userMessage = chatInput.value.trim();
      if (!userMessage) return;

      addMessage(userMessage, "user");
      chatInput.value = "";

      const selectedModel = aiFunctionalitySelect.value; // Still sent to server (if needed)

      try {
        const payload = {
          message: userMessage,
          conversation_id: sessionId, // Use the stored session ID as conversation ID
        };

        const response = await fetch("http://0.0.0.0:8080/api/v1/chat", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(payload),
        });

        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        addMessage(data.response, "bot");

        // No need to update conversationId here - it's the same as sessionId
      } catch (error) {
        console.error("Error:", error);
        addMessage("Error connecting to server.", "bot");
      }
    };

    sendBtn.addEventListener("click", sendMessage);

    chatInput.addEventListener("keyup", (event) => {
      if (event.key === "Enter") {
        sendMessage();
      }
    });

    function generateSessionId() {
      return "xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx".replace(/[xy]/g, (c) => {
        const r = (Math.random() * 16) | 0,
          v = c === "x" ? r : (r & 0x3) | 0x8;
        return v.toString(16);
      });
    }
  });
