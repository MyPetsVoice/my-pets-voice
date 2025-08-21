function switchTab(tabName) {
  // 모든 탭 비활성화
  document.querySelectorAll(".nav-tab").forEach((tab) => {
    tab.classList.remove("active");
  });
  document.querySelectorAll(".tab-content").forEach((content) => {
    content.classList.remove("active");
  });

  // 선택된 탭 활성화
  event.target.classList.add("active");
  document.getElementById(tabName + "-tab").classList.add("active");
}

function openModal(type) {
  document.getElementById(type + "-modal").style.display = "block";
}

function closeModal(modalId) {
  document.getElementById(modalId).style.display = "none";
}

function openChat() {
  document.getElementById("chat-overlay").style.display = "block";
}

function closeChat() {
  document.getElementById("chat-overlay").style.display = "none";
}

function openAnalysis() {
  document.getElementById("analysis-page").style.display = "block";
}

function closeAnalysis() {
  document.getElementById("analysis-page").style.display = "none";
}

function sendMessage() {
  const input = document.getElementById("chatInput");
  const messages = document.getElementById("chatMessages");

  if (input.value.trim()) {
    // 사용자 메시지 추가
    const userMessage = document.createElement("div");
    userMessage.className = "message user";
    userMessage.textContent = input.value;
    messages.appendChild(userMessage);

    // 입력 초기화
    const userText = input.value;
    input.value = "";

    // AI 응답 시뮬레이션
    setTimeout(() => {
      const aiMessage = document.createElement("div");
      aiMessage.className = "message ai";
      aiMessage.innerHTML = getAIResponse(userText);
      messages.appendChild(aiMessage);

      // 스크롤을 맨 아래로
      messages.scrollTop = messages.scrollHeight;
    }, 1000);

    // 스크롤을 맨 아래로
    messages.scrollTop = messages.scrollHeight;
  }
}

function getAIResponse(userText) {
  const responses = {
    설사: "설사가 계속된다면 탈수 위험이 있어요. 물을 충분히 주시고, 12시간 정도 금식 후 소량의 흰쌀밥부터 시작해보세요. 24시간 이상 지속되면 병원 방문을 권해드려요.",
    열: "체온이 39도 이상이라면 응급상황일 수 있어요. 시원한 곳에서 휴식을 취하게 하고, 물수건으로 발바닥과 귀를 시원하게 해주세요. 즉시 병원에 연락하세요.",
    식욕: "갑작스런 식욕 부진은 여러 원인이 있을 수 있어요. 스트레스, 환경 변화, 또는 건강 문제일 수 있습니다. 2일 이상 지속되면 수의사 상담을 받아보세요.",
    구토: "구토가 반복된다면 위험할 수 있어요. 일시적으로 물과 사료를 제한하고, 증상이 계속되면 즉시 병원에 가세요. 탈수 방지가 중요해요.",
  };

  for (let keyword in responses) {
    if (userText.includes(keyword)) {
      return responses[keyword];
    }
  }

  return "반려동물의 건강에 관한 구체적인 증상을 알려주시면 더 정확한 답변을 드릴 수 있어요. 응급상황이라면 즉시 가까운 동물병원에 연락하세요! 🏥";
}

function handleChatKeyPress(event) {
  if (event.key === "Enter") {
    sendMessage();
  }
}

// 반려동물 선택 기능
document.querySelectorAll(".pet-card").forEach((card) => {
  card.addEventListener("click", function () {
    document
      .querySelectorAll(".pet-card")
      .forEach((c) => c.classList.remove("active"));
    this.classList.add("active");
  });
});

let today = dayjs();
let current = dayjs();

const monthLabel = document.getElementById("current-month");
const grid = document.getElementById("calendar-grid");

function renderCalendar(date) {
  monthLabel.textContent = date.format("YYYY년 M월");

  // 기존 날짜 지우기 (요일 헤더 제외)
  grid.querySelectorAll(".calendar-day").forEach((e) => e.remove());

  const firstDay = date.startOf("month").day(); // 0=일요일
  const lastDate = date.endOf("month").date();

  // 빈칸
  for (let i = 0; i < firstDay; i++) {
    grid.appendChild(document.createElement("div"));
  }

  // 날짜
  for (let d = 1; d <= lastDate; d++) {
    const cell = document.createElement("div");
    cell.textContent = d;
    cell.classList.add("calendar-day");

    if (
      date.year() === today.year() &&
      date.month() === today.month() &&
      d === today.date()
    ) {
      cell.classList.add("today");
    }

    grid.appendChild(cell);
  }
}

document.getElementById("prev-month").onclick = () => {
  current = current.subtract(1, "month");
  renderCalendar(current);
};
document.getElementById("next-month").onclick = () => {
  current = current.add(1, "month");
  renderCalendar(current);
};

renderCalendar(current);
