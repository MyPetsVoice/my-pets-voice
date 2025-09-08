function getCurrentPetId() {
    return localStorage.getItem('currentPetId')
}

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

  const pet_id = getCurrentPetId();

  // 로딩 메시지 추가
  const loadingMessage = document.createElement("div");
  loadingMessage.className = "message ai loading";
  loadingMessage.textContent = "🤖 답변을 준비중입니다...";
  messages.appendChild(loadingMessage);
  messages.scrollTop = messages.scrollHeight;

  try {
    // Flask API 호출
    const response = await fetch("/api/dailycares/care-chatbot", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        message: userText,
        pet_id: pet_id,
      }),
    });

    if (!response.ok) throw new Error("서버 응답 오류");

    const data = await response.json();

    // 로딩 메시지를 실제 응답으로 교체
    loadingMessage.innerHTML = formatChatbotResponse(
      marked.parse(data.response || "응답을 가져오지 못했습니다.")
    );
    loadingMessage.classList.remove("loading");
  } catch (error) {
    console.error("Error:", error);
    loadingMessage.textContent =
      "서버 연결 문제. 잠시 후 다시 시도해주세요.";
    loadingMessage.classList.remove("loading");
  }
}


function handleChatKeyPress(event) {
  if (event.key === "Enter") sendMessage();
}

function formatChatbotResponse(text) {
  // 줄바꿈 보정
  let formatted = text.replace(/\n/g, "<br>");

  // **볼드** 처리
  formatted = formatted.replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>");

  // 불필요한 중복 <br> 제거
  formatted = formatted.replace(/(<br>\s*){2,}/g, "<br>");

  return formatted;
}

async function petInfo(pet_id) {
  try {
    const response = await fetch(`/api/dailycares/pet-info/${pet_id}`);
    const pet_detail = document.getElementById("pet_detail");

    if (!response.ok) {
      if (pet_detail)
        pet_detail.innerHTML = "<p>Pet 정보를 불러올 수 없습니다.</p>";
      return;
    }

    const petData = await response.json();
    console.log("ai건강상담", petData);

    // 모달 헤더 옆에도 이름+나이 표시
    const headerInfo = document.getElementById("pet-info-header");
    if (headerInfo) {
      headerInfo.textContent = `(${petData.pet_name || "정보 없음"}, ${
        petData.pet_age || "?"
      }살)`;
    }
  } catch (error) {
    console.error("Pet Info Error:", error);
  }
}
