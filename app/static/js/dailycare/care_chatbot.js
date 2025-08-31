
async function sendMessage() {
  const input = document.getElementById("chatInput");
  const messages = document.getElementById("chatMessages");
  const userText = input.value.trim();
  if (!userText) return;

  // 사용자 메시지 추가
  const userMessage = document.createElement("div");
  userMessage.className = "message user";
  userMessage.textContent = userText;
  messages.appendChild(userMessage);
  input.value = "";

  messages.scrollTop = messages.scrollHeight;

  try {
    // Flask API 호출
    const response = await fetch("/api/dailycares/care-chatbot", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({
        message: userText,
        pet_id: 1,   // 실제 선택된 pet_id로 교체 가능
        user_id: 1   // 로그인된 user_id로 교체 가능
      })
    });

    const data = await response.json();

    // AI 응답 메시지 추가
    const aiMessage = document.createElement("div");
    aiMessage.className = "message ai";
    aiMessage.innerHTML = data.response || "응답을 가져오지 못했습니다.";
    messages.appendChild(aiMessage);
    messages.scrollTop = messages.scrollHeight;

  } catch (error) {
    console.error("Error:", error);
    const errorMessage = document.createElement("div");
    errorMessage.className = "message ai";
    errorMessage.textContent = "서버 연결에 문제가 생겼어요. 잠시 후 다시 시도해주세요.";
    messages.appendChild(errorMessage);
  }
}

function handleChatKeyPress(event) {
  if (event.key === "Enter") sendMessage();
}

