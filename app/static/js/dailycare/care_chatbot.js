
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
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        message: userText,
        pet_id: 1,
        user_id: 1,
      }),
    });

    const data = await response.json();

    // AI 응답 메시지 추가
    const aiMessage = document.createElement("div");
    aiMessage.className = "message ai";
  aiMessage.innerHTML = formatChatbotResponse(
    marked.parse(data.response || "응답을 가져오지 못했습니다.")
  );
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


function formatChatbotResponse(text) {
  // 1. 줄바꿈 변환
  let formatted = text.replace(/\n/g, "<br>");

  // 2. **볼드** 변환
  formatted = formatted.replace(
    /\*\*(.*?)\*\*/g,
    "<br><strong>$1</strong><br>"
  );

  // 3. 중복 <br> 정리
  formatted = formatted.replace(/(<br>\s*){2,}/g, "<br>");

  return formatted;
}