// index.js

// 전역 변수
let selectedPetPersonaId = null;
let allDiaries = [];
let currentUser = { user_id: 1 }; // 임시 사용자

// 페이지 로드 시 초기화
document.addEventListener("DOMContentLoaded", async function () {
  await setupEventListeners();
  await loadUserPets();
});

// 이벤트 리스너 설정
async function setupEventListeners() {
  // 검색 입력 이벤트
  document.getElementById("searchInput").addEventListener("keyup", searchDiary);

  // 검색 입력 엔터키 이벤트
  document
    .getElementById("searchInput")
    .addEventListener("keypress", function (e) {
      if (e.key === "Enter") {
        searchDiary();
      }
    });
}

// 사용자의 펫 목록
async function loadUserPets() {
  const response = await fetch(`/api/diary/personas/1`);
  const data = await response.json();

  const petList = document.getElementById("petList");
  const loadingMsg = document.getElementById("petLoadingMsg");

  if (data.success && data.personas.length > 0) {
    loadingMsg.remove();

    data.personas.forEach((persona) => {
      const petCard = createPetCard(persona);
      petList.appendChild(petCard);
    });

    // 펫 추가 버튼 생성
    const addButton = createPetAddButton();
    petList.appendChild(addButton);
  } else {
    loadingMsg.innerHTML =
      '<p class="text-red-500">등록된 반려동물이 없습니다.</p>';
  }
}

// 펫 카드 생성
function createPetCard(persona) {
  const div = document.createElement("div");
  div.className =
    "pet-card p-4 rounded-xl bg-gradient-to-r from-orange-100 to-yellow-100 hover:from-orange-200 hover:to-yellow-200 transition-all duration-300";
  div.dataset.petPersonaId = persona.pet_persona_id;

  // 종류에 따른 이모지 설정 (추가 수정 중...)
  const emoji =
    persona.pet_species === "개"
      ? "🐕"
      : persona.pet_species === "고양이"
      ? "🐈"
      : "🐾";

  div.innerHTML = `
        <div class="flex items-center space-x-3">
            <div class="pet-emoji w-12 h-12 rounded-full bg-gradient-to-br from-orange-400 to-yellow-400 flex items-center justify-center text-white font-bold text-lg shadow-lg">
                ${emoji}
            </div>
            <div>
                <h3 class="font-semibold text-gray-800">${persona.pet_name}</h3>
                <p class="text-xs text-gray-600 diary-count">일기 로딩중...</p>
            </div>
        </div>
    `;

  // 클릭 이벤트
  div.addEventListener("click", function () {
    selectPet(persona.pet_persona_id, persona.pet_name);
  });

  return div;
}

// 펫 추가 버튼 생성
function createPetAddButton() {
  const div = document.createElement("div");
  div.className =
    "pet-add-btn p-4 rounded-xl border-2 border-dashed border-gray-300 transition-all duration-300";

  div.innerHTML = `
        <div class="flex items-center justify-center space-x-2 text-gray-500">
            <i class="fas fa-plus-circle text-2xl"></i>
            <span class="font-medium">펫 추가하기</span>
        </div>
    `;

  // 펫 작성 페이지로 이동
  div.addEventListener("click", function () {
    window.location.href = "/mypage";
  });

  return div;
}

// 펫 선택
async function selectPet(petPersonaId, petName) {
  // 모든 펫 카드 비활성화
  document.querySelectorAll(".pet-card").forEach((card) => {
    card.classList.remove("active");
  });

  // 선택된 펫 카드 활성화
  const selectedCard = document.querySelector(
    `[data-pet-persona-id="${petPersonaId}"]`
  );
  selectedCard.classList.add("active");

  // 선택된 펫 정보 업데이트
  selectedPetPersonaId = petPersonaId;
  document.getElementById("selectedPetName").textContent = petName;
  document.getElementById("selectedPetInfo").style.display = "block";

  console.log(`선택한펫: ${petName} (ID: ${petPersonaId})`);

  // 해당 펫의 일기 목록 로드
  await loadPetDiaries(petPersonaId);
}

// 특정 펫의 일기 목록 로드
async function loadPetDiaries(petPersonaId) {
  const tableBody = document.getElementById("diaryTableBody");
  const loadingMsg = document.getElementById("diaryLoadingMsg");

  // 로딩 표시
  tableBody.innerHTML = `
        <tr>
            <td colspan="4" class="text-center py-8 text-gray-500">
                <i class="fas fa-spinner fa-spin mr-2"></i>
                일기를 불러오는 중...
            </td>
        </tr>
    `;

  const response = await fetch(`/api/diary/list/${petPersonaId}`);
  const data = await response.json();

  if (data.success && data.diaries.length > 0) {
    allDiaries = data.diaries;
    displayDiaries(data.diaries);

    // 일기 수 업데이트
    updateDiaryCount(petPersonaId, data.diaries.length);

    // 페이지네이션 표시
    document.getElementById("pagination").style.display = "flex";
  } else {
    tableBody.innerHTML = `
            <tr>
                <td colspan="4" class="empty-state">
                    <i class="fas fa-book-open"></i>
                    <p>아직 작성된 일기가 없습니다.</p>
                    <p class="text-sm mt-2">첫 번째 일기를 작성해보세요!</p>
                </td>
            </tr>
        `;
  }
}

// 일기 목록 표시
function displayDiaries(diaries) {
  const tableBody = document.getElementById("diaryTableBody");

  tableBody.innerHTML = diaries
    .map(
      (diary, index) => `
        <tr class="diary-row border-b hover:bg-orange-50 transition-colors duration-200" onclick="location.href='/diary/detail/${
          diary.diary_id
        }'">
            <td class="py-4 px-4 text-gray-600">${index + 1}</td>
            <td class="py-4 px-4">
                <div class="flex items-center space-x-2">
                    <span class="font-medium text-gray-800">${
                      diary.title
                    }</span>
                    ${
                      diary.content_ai
                        ? '<span class="ai-badge text-xs px-2 py-1 bg-yellow-100 text-yellow-700 rounded-full">AI</span>'
                        : ""
                    }
                </div>
            </td>
            <td class="py-4 px-4 text-gray-600">${formatDate(
              diary.diary_date
            )}</td>
            <td class="py-4 px-4 text-center">
                <span class="text-2xl">${diary.mood || "😊"}</span>
            </td>
        </tr>
    `
    )
    .join("");
}

// 일기 수 업데이트
function updateDiaryCount(petPersonaId, count) {
  const petCard = document.querySelector(
    `[data-pet-persona-id="${petPersonaId}"]`
  );
  if (petCard) {
    const countElement = petCard.querySelector(".diary-count");
    countElement.textContent = `일기 ${count}개`;
  }
}

// 일기 검색
function searchDiary() {
  const searchValue = document
    .getElementById("searchInput")
    .value.toLowerCase();

  if (!selectedPetPersonaId) {
    alert("먼저 반려동물을 선택해주세요.");
    return;
  }

  if (searchValue === "") {
    displayDiaries(allDiaries);
    return;
  }

  const filteredDiaries = allDiaries.filter(
    (diary) =>
      diary.title.toLowerCase().includes(searchValue) ||
      (diary.content_user &&
        diary.content_user.toLowerCase().includes(searchValue)) ||
      (diary.content_ai && diary.content_ai.toLowerCase().includes(searchValue))
  );

  displayDiaries(filteredDiaries);

  if (filteredDiaries.length === 0) {
    const tableBody = document.getElementById("diaryTableBody");
    tableBody.innerHTML = `
            <tr>
                <td colspan="4" class="empty-state">
                    <i class="fas fa-search"></i>
                    <p>"${searchValue}"에 대한 검색 결과가 없습니다.</p>
                </td>
            </tr>
        `;
  }
}

// 날짜 포맷팅
function formatDate(dateString) {
  const date = new Date(dateString);
  const year = date.getFullYear();
  const month = String(date.getMonth() + 1).padStart(2, "0");
  const day = String(date.getDate()).padStart(2, "0");
  return `${year}-${month}-${day}`;
}
