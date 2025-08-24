// AI 메시지 전송
function sendMessage() {
  const input = document.getElementById("chatInput");
  const messages = document.getElementById("chatMessages");
  const userText = input.value.trim();
  if (!userText) return;

  // 사용자 메시지
  const userMessage = document.createElement("div");
  userMessage.className = "message user";
  userMessage.textContent = userText;
  messages.appendChild(userMessage);
  input.value = "";

  // AI 응답 시뮬레이션
  setTimeout(() => {
    const aiMessage = document.createElement("div");
    aiMessage.className = "message ai";
    aiMessage.innerHTML = getAIResponse(userText);
    messages.appendChild(aiMessage);
    messages.scrollTop = messages.scrollHeight;
  }, 500);

  messages.scrollTop = messages.scrollHeight;
}

// AI 응답 처리
function getAIResponse(userText) {
  const responses = {
    설사: "설사가 계속된다면 탈수 위험이 있어요...",
    열: "체온이 39도 이상이라면 응급상황일 수 있어요...",
    식욕: "갑작스런 식욕 부진은 여러 원인이 있을 수 있어요...",
    구토: "구토가 반복된다면 위험할 수 있어요...",
  };

  for (let key in responses) {
    if (userText.includes(key)) return responses[key];
  }

  return "반려동물의 건강에 관한 구체적인 증상을 알려주시면 더 정확한 답변을 드릴 수 있어요.";
}

function handleChatKeyPress(event) {
  if (event.key === "Enter") sendMessage();
}
