// 전역 변수
let selectedPetPersonaId = null;
let currentAIContent = null;

// 페이지 로드 시 초기화
document.addEventListener("DOMContentLoaded", async function () {
  // 오늘 날짜 설정
  const today = new Date().toISOString().split("T")[0];
  document.getElementById("diaryDate").value = today;

  // 이벤트 리스너 등록
  await setupEventListeners();

  // 사용자의 펫 페르소나 로드
  await loadUserPersonas();
});

// 이벤트 리스너 설정
async function setupEventListeners() {
  // 사진 업로드 영역 클릭
  document.getElementById("uploadArea").addEventListener("click", function () {
    document.getElementById("photos").click();
  });

  // 파일 선택 이벤트
  document
    .getElementById("photos")
    .addEventListener("change", handleFileSelect);

  // AI 변환 버튼
  document
    .getElementById("aiConvertBtn")
    .addEventListener("click", convertToAI);

  // 적용하기 버튼
  document.getElementById("applyBtn").addEventListener("click", applyAIContent);

  // 다시하기 버튼
  document.getElementById("retryBtn").addEventListener("click", convertToAI);

  // 취소 버튼
  document.getElementById("cancelBtn").addEventListener("click", function () {
    if (confirm("작성 중인 내용이 사라집니다. 정말 취소하시겠습니까?")) {
      history.back();
    }
  });

  // 폼 제출
  document.getElementById("diaryForm").addEventListener("submit", submitDiary);
}

// 사용자의 펫 페르소나 로드
async function loadUserPersonas() {
  const response = await fetch(`/api/diary/personas`);
  const data = await response.json();

  const petSelection = document.getElementById("petSelection");
  const loadingMsg = document.getElementById("petLoadingMsg");

  if (data.success && data.personas.length > 0) {
    loadingMsg.remove();

    data.personas.forEach((persona) => {
      const petCard = createPetCard(persona);
      petSelection.appendChild(petCard);
    });
  } else {
    loadingMsg.innerHTML =
      '<p class="text-red-500">등록된 반려동물이 없습니다.</p>';
  }
}

// 펫 카드 생성
function createPetCard(persona) {
  const div = document.createElement("div");
  div.className =
    "pet-option cursor-pointer p-4 rounded-xl border-2 border-gray-200 hover:border-orange-400 transition-all duration-300";
  div.dataset.petPersonaId = persona.pet_persona_id;

  // 이모지 설정 (프로필로 변경 예정)
  const emoji =
    persona.pet_species === "개"
      ? "🐕"
      : persona.pet_species === "고양이"
      ? "🐈"
      : "🐾";

  div.innerHTML = `
        <div class="flex items-center space-x-3">
            <div class="w-12 h-12 rounded-full bg-gradient-to-br from-orange-400 to-yellow-400 flex items-center justify-center text-white font-bold text-lg">
                ${emoji}
            </div>
            <div>
                <h3 class="font-semibold text-gray-800">${persona.pet_name}</h3>
                <p class="text-xs text-gray-600">${persona.pet_species} · ${
    persona.pet_breed || "믹스"
  }</p>
            </div>
        </div>
    `;

  // 클릭 이벤트
  div.addEventListener("click", function () {
    selectPetPersona(persona.pet_persona_id, persona.pet_name);
  });

  return div;
}

// 펫 페르소나 선택
function selectPetPersona(petPersonaId, petName) {
  // 모든 펫 카드 비활성화
  document.querySelectorAll(".pet-option").forEach((card) => {
    card.classList.remove("selected");
  });

  // 선택된 펫 카드 활성화
  const selectedCard = document.querySelector(
    `[data-pet-persona-id="${petPersonaId}"]`
  );
  selectedCard.classList.add("selected");

  // 선택된 펫 페르소나 ID 저장
  selectedPetPersonaId = petPersonaId;
  document.getElementById("selectedPetPersonaId").value = petPersonaId;

  console.log(`선택한 페르소나: ${petName} (ID: ${petPersonaId})`);
}

// 파일 선택 처리
function handleFileSelect(event) {
  const files = event.target.files;
  const preview = document.getElementById("photoPreview");
  preview.innerHTML = "";

  for (let i = 0; i < files.length; i++) {
    const file = files[i];
    if (file.type.startsWith("image/")) {
      const reader = new FileReader();
      reader.onload = function (e) {
        const div = document.createElement("div");
        div.className = "photo-preview-item";
        div.innerHTML = `
                    <img src="${e.target.result}" class="w-full h-24 object-cover rounded-lg border border-gray-200">
                    <button type="button" class="photo-remove-btn" onclick="removePhoto(this)">×</button>
                    <div class="text-xs text-gray-500 mt-1 truncate">${file.name}</div>
                `;
        preview.appendChild(div);
      };
      reader.readAsDataURL(file);
    }
  }
}

// 사진 제거
function removePhoto(button) {
  button.parentElement.remove();
}

// AI 변환 함수
async function convertToAI() {
  const content = document.getElementById("content").value.trim();

  if (!content) {
    alert("일기 내용을 먼저 작성해주세요.");
    return;
  }

  if (!selectedPetPersonaId) {
    alert("반려동물을 선택해주세요.");
    return;
  }

  // 로딩 상태 표시
  document.getElementById("aiLoading").classList.remove("hidden");
  document.getElementById("aiResult").classList.add("hidden");
  document.getElementById("aiConvertBtn").disabled = true;

  const response = await fetch("/api/diary/convert-ai", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      content: content,
      pet_persona_id: selectedPetPersonaId,
    }),
  });

  const data = await response.json();

  // 로딩 상태 해제
  document.getElementById("aiLoading").classList.add("hidden");
  document.getElementById("aiConvertBtn").disabled = false;

  if (data.success) {
    currentAIContent = data.ai_content;

    // AI 결과 표시
    document.getElementById("aiContent").textContent = currentAIContent;
    document.getElementById("aiResult").classList.remove("hidden");
  } else {
    alert(`AI 변환 실패: ${data.message}`);
  }
}

// AI 내용 적용
function applyAIContent() {
  if (currentAIContent) {
    document.getElementById("finalContentText").textContent = currentAIContent;
    document.getElementById("finalContentInput").value = currentAIContent;
    document.getElementById("finalContent").classList.remove("hidden");

    // 원본 내용 영역 읽기 전용으로 변경
    const originalContent = document.getElementById("content");
    originalContent.style.backgroundColor = "#f9fafb";
    originalContent.readOnly = true;

    alert("반려동물 관점의 일기가 적용되었습니다!");
  }
}

// 폼 제출
async function submitDiary(event) {
  event.preventDefault();

  if (!selectedPetPersonaId) {
    alert("반려동물을 선택해주세요.");
    return;
  }

  const formData = new FormData(event.target);

  const response = await fetch("/api/diary/create", {
    method: "POST",
    body: formData,
  });

  const data = await response.json();

  if (data.success) {
    alert("일기가 성공적으로 저장되었습니다!");
    window.location.href = "/diary/";
  } else {
    alert(`저장 실패: ${data.message}`);
  }
}
