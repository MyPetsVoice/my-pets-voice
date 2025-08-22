// 탭 전환
function switchTab(event, tabName) {
  document
    .querySelectorAll(".nav-tab")
    .forEach((tab) => tab.classList.remove("active"));
  document
    .querySelectorAll(".tab-content")
    .forEach((content) => content.classList.remove("active"));

  event.target.classList.add("active");
  document.getElementById(tabName + "-tab").classList.add("active");
}
// open modal
function openModal(name) {
  console.log(`##### name ${name}`)
  fetch(`/dailycare/modal/${name}`)
    .then((res) => {
      if (!res.ok) throw new Error("네트워크 오류");
      return res.text();
    })
    .then((html) => {
      console.log(`##### html ${html}`);
      const modal = document.getElementById("common-modal");
      const content = modal.querySelector("#modalContent");

      content.innerHTML = html; // AJAX 내용 삽입
      modal.classList.remove("hidden"); // 모달 표시

      // 닫기 버튼 이벤트
      const closeBtn = document.getElementById("modal-close-btn");
      closeBtn.onclick = () => modal.classList.add("hidden");
     
    })
    .catch((err) => {
      console.error("모달 불러오기 실패:", err);
      alert("모달을 불러오지 못했습니다.");
    });
}



// close modal
function closeModal() {
  document.getElementById("common-modal").classList.add("hidden");
}


// 분석 페이지 열기/닫기
function openAnalysis() {
  document.getElementById("analysis-page").style.display = "block";
}
function closeAnalysis() {
  document.getElementById("analysis-page").style.display = "none";
}

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

// 반려동물 선택 기능
document.querySelectorAll(".pet-card").forEach((card) => {
  card.addEventListener("click", function () {
    document
      .querySelectorAll(".pet-card")
      .forEach((c) => c.classList.remove("active"));
    this.classList.add("active");
  });
});

// 달력 렌더링
let today = dayjs();
let current = dayjs();
const monthLabel = document.getElementById("current-month");
const grid = document.getElementById("calendar-grid");

function renderCalendar(date) {
  monthLabel.textContent = date.format("YYYY년 M월");
  grid.querySelectorAll(".calendar-day").forEach((e) => e.remove());

  const firstDay = date.startOf("month").day();
  const lastDate = date.endOf("month").date();

  for (let i = 0; i < firstDay; i++)
    grid.appendChild(document.createElement("div"));

  for (let d = 1; d <= lastDate; d++) {
    const cell = document.createElement("div");
    cell.textContent = d;
    cell.classList.add("calendar-day");
    if (
      date.year() === today.year() &&
      date.month() === today.month() &&
      d === today.date()
    )
      cell.classList.add("today");
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
