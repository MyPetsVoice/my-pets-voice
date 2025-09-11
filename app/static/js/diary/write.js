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
  try {
    const response = await fetch(`/api/diary/personas`);
    const data = await response.json();

    const petSelection = document.getElementById("petSelection");
    const loadingMsg = document.getElementById("petLoadingMsg");

    if (data.success && data.personas.length > 0) {
      loadingMsg.remove();

      // URL 파라미터에서 미리 선택된 펫 ID 가져오기
      const urlParams = new URLSearchParams(window.location.search);
      const preSelectedPetId = urlParams.get("pet_id");

      if (preSelectedPetId) {
        // 미리 선택된 펫이 있으면 해당 펫 정보만 표시
        const selectedPersona = data.personas.find(
          (p) => p.pet_persona_id == preSelectedPetId
        );
        if (selectedPersona) {
          showSelectedPetInfo(selectedPersona);
          selectedPetPersonaId = preSelectedPetId;
          document.getElementById("selectedPetPersonaId").value =
            preSelectedPetId;

          // URL에서 파라미터 제거
          const newUrl = window.location.pathname;
          window.history.replaceState({}, document.title, newUrl);
          return;
        }
      }

      // 미리 선택된 펫이 없으면 기존 방식으로 선택 UI 표시
      data.personas.forEach((persona) => {
        const petCard = createPetCard(persona);
        petSelection.appendChild(petCard);
      });
    } else if (!data.success && data.message === "로그인이 필요합니다.") {
      alert("로그인 세션이 만료되었습니다. 다시 로그인해주세요.");
      window.location.href = "/login";
    } else {
      loadingMsg.innerHTML =
        '<p class="text-red-500 text-center">등록된 반려동물이 없습니다.<br><a href="/mypage" class="text-orange-500 underline">반려동물을 먼저 등록해주세요</a></p>';
    }
  } catch (error) {
    console.error("펫 목록 로드 실패:", error);
    const loadingMsg = document.getElementById("petLoadingMsg");
    loadingMsg.innerHTML =
      '<p class="text-red-500 text-center">펫 목록을 불러오는데 실패했습니다.</p>';
  }
}

// 선택된 펫 정보 표시 (펫 선택 UI 숨기고 정보만 표시)
function showSelectedPetInfo(persona) {
  const petSelectionSection = document.querySelector(".mb-6"); // 펫 선택 섹션

  const emoji =
    persona.pet_species === "개"
      ? "🐕"
      : persona.pet_species === "고양이"
      ? "🐈"
      : "🐾";

  petSelectionSection.innerHTML = `
    <label class="block text-sm font-semibold text-gray-700 mb-3">
      <i class="fas fa-paw text-orange-400 mr-2"></i>
      선택된 반려동물
    </label>
    <div class="bg-gradient-to-r from-orange-100 to-yellow-100 rounded-xl p-4 border border-orange-200">
      <div class="flex items-center space-x-3">
        <div class="w-12 h-12 rounded-full bg-gradient-to-br from-orange-400 to-yellow-400 flex items-center justify-center text-white font-bold text-lg">
          ${emoji}
        </div>
        <div>
          <h3 class="font-semibold text-gray-800">${persona.pet_name}</h3>
          <p class="text-sm text-gray-600">${persona.pet_species} · ${
    persona.pet_breed || "믹스"
  }</p>
        </div>
        <div class="ml-auto">
        </div>
      </div>
    </div>
    <input type="hidden" id="selectedPetPersonaId" name="pet_persona_id" value="${
      persona.pet_persona_id
    }" required />
  `;
}

// 펫 선택 UI 다시 보여주기 (변경하기 버튼 클릭시)
async function showPetSelection() {
  const petSelectionSection = document.querySelector(".mb-6");
  petSelectionSection.innerHTML = `
    <label class="block text-sm font-semibold text-gray-700 mb-3">
      <i class="fas fa-paw text-orange-400 mr-2"></i>
      반려동물 선택
    </label>
    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4" id="petSelection">
      <div id="petLoadingMsg" class="col-span-full text-center text-gray-500">
        <i class="fas fa-spinner fa-spin mr-2"></i>
        반려동물 정보를 불러오는 중...
      </div>
    </div>
    <input type="hidden" id="selectedPetPersonaId" name="pet_persona_id" required />
  `;

  // 초기화
  selectedPetPersonaId = null;

  // 펫 목록 다시 로드
  await loadUserPersonas();
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
                    <img src="${e.target.result}" alt="" class="w-full h-24 object-cover rounded-lg border border-gray-200" onerror="this.parentElement.style.display='none'">
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
  document.getElementById("finalContent").classList.add("hidden"); // 기존 최종 내용 숨김
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

    // 바로 최종 일기 내용에 적용
    document.getElementById("finalContentText").textContent = currentAIContent;
    document.getElementById("finalContentInput").value = currentAIContent;
    document.getElementById("finalContent").classList.remove("hidden");

    // 원본 내용 영역 읽기 전용으로 변경
    const originalContent = document.getElementById("content");
    originalContent.style.backgroundColor = "#f9fafb";
    originalContent.readOnly = true;
  } else {
    alert(`AI 변환 실패: ${data.message}`);
  }
}

// AI 필수 js
async function submitDiary(event) {
  event.preventDefault();

  if (!selectedPetPersonaId) {
    alert("반려동물을 선택해주세요.");
    return;
  }

  // AI 변환이 완료되었는지 확인
  if (!currentAIContent) {
    alert("AI 변환을 먼저 진행해주세요. '너의 목소리로' 버튼을 눌러주세요.");
    return;
  }

  // content_ai가 있는지 확인
  const contentAi = document.getElementById("finalContentInput").value;
  if (!contentAi || contentAi.trim() === "") {
    alert("AI 변환된 일기 내용이 없습니다. '너의 목소리로' 버튼을 눌러주세요.");
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
    window.location.href = "/diary";
  } else {
    alert(`저장 실패: ${data.message}`);
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
    window.location.href = "/diary";
  } else {
    alert(`저장 실패: ${data.message}`);
  }
}
