let selectedPetPersonaId = null;
let allDiaries = [];
let currentPage = 1; // 현재 페이지 추가
let totalPages = 1; // 총 페이지 수 추가

// 페이지 로드 시 초기화
document.addEventListener("DOMContentLoaded", async function () {
  await setupEventListeners(); //검색창, 버튼
  await loadUserPets(); //내 펫 불러오기
  // 전체 일기를 먼저 로드
  await loadAllDiaries();
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

  // 일기 추가 버튼 이벤트 추가
  const addDiaryBtn = document.getElementById("addDiaryBtn");
  if (addDiaryBtn) {
    addDiaryBtn.addEventListener("click", function () {
      goToWritePage();
    });
  }

  // "전체 일기" 버튼 이벤트 (있다면)
  const showAllButton = document.getElementById("showAllDiariesBtn");
  if (showAllButton) {
    showAllButton.addEventListener("click", showAllDiaries);
  }
}

// 일기 작성 페이지로 이동하는 함수
function goToWritePage() {
  let writeUrl = "/diary/write";

  // 선택된 펫이 있다면 URL에 펫 ID 추가
  if (selectedPetPersonaId && selectedPetPersonaId !== "all") {
    writeUrl += `?pet_id=${selectedPetPersonaId}`;
  }

  window.location.href = writeUrl;
}

// 전체 일기 로드 (페이징 추가)
async function loadAllDiaries(page = 1) {
  try {
    const tableBody = document.getElementById("diaryTableBody");

    // 로딩 표시
    tableBody.innerHTML = `
      <tr>
        <td colspan="4" class="text-center py-8 text-gray-500">
          <i class="fas fa-spinner fa-spin mr-2"></i>
          전체 일기를 불러오는 중...
        </td>
      </tr>
    `;

    const response = await fetch(`/api/diary/list?page=${page}`);
    const data = await response.json();

    if (data.success && data.diaries.length > 0) {
      allDiaries = data.diaries;
      currentPage = data.pagination.current_page;
      totalPages = data.pagination.total_pages;

      displayAllDiaries(data.diaries);
      updatePagination(data.pagination, "all");

      // 전체 일기 표시 상태로 설정
      document.getElementById("selectedPetName").textContent = "전체 일기";
      document.getElementById("selectedPetInfo").style.display = "block";
    } else {
      tableBody.innerHTML = `
        <tr>
          <td colspan="4" class="empty-state text-center py-8">
            <i class="fas fa-book-open text-4xl text-gray-300 mb-4"></i>
            <p class="text-gray-500 font-medium">아직 작성된 일기가 없습니다.</p>
            <p class="text-sm text-gray-400 mt-2">첫 번째 일기를 작성해보세요!</p>
          </td>
        </tr>
      `;
      hidePagination();
    }
  } catch (error) {
    console.error("전체 일기 로드 실패:", error);
    const tableBody = document.getElementById("diaryTableBody");
    tableBody.innerHTML = `
      <tr>
        <td colspan="4" class="text-center py-8 text-red-500">
          <i class="fas fa-exclamation-triangle mr-2"></i>
          일기 목록을 불러오는데 실패했습니다.
        </td>
      </tr>
    `;
    hidePagination();
  }
}

// 전체 일기 표시
function displayAllDiaries(diaries) {
  const tableBody = document.getElementById("diaryTableBody");

  if (!diaries || diaries.length === 0) {
    tableBody.innerHTML = `
      <tr>
        <td colspan="4" class="empty-state text-center py-8">
          <i class="fas fa-book-open text-4xl text-gray-300 mb-4"></i>
          <p class="text-gray-500 font-medium">일기가 없습니다.</p>
        </td>
      </tr>
    `;
    return;
  }

  tableBody.innerHTML = diaries
    .map(
      (diary, index) => `
        <tr class="diary-row border-b hover:bg-orange-50 transition-colors duration-200 cursor-pointer" onclick="viewDiaryDetail(${
          diary.diary_id
        })">
          <td class="py-4 px-4 text-gray-600">${
            (currentPage - 1) * 5 + index + 1
          }</td>
          <td class="py-4 px-4">
            <div class="flex flex-col space-y-1">
              <div class="flex items-center space-x-2">
                <span class="font-medium text-gray-800">${diary.title}</span>
              </div>
            
            </div>
          </td>
          <td class="py-4 px-4 text-gray-600">${formatDate(
            diary.diary_date
          )}</td>
          <td class="py-4 px-4 text-center">
            <span class="text-2xl">${diary.mood}</span>
          </td>
        </tr>
      `
    )
    .join("");
}

// 사용자의 펫 목록
async function loadUserPets() {
  try {
    const response = await fetch(`/api/diary/personas`);
    const data = await response.json();

    const petList = document.getElementById("petList");
    const loadingMsg = document.getElementById("petLoadingMsg");

    if (data.success && data.personas.length > 0) {
      loadingMsg.remove();

      // 전체 일기 버튼 추가
      const allDiariesButton = createAllDiariesButton();
      petList.appendChild(allDiariesButton);

      data.personas.forEach((persona) => {
        const petCard = createPetCard(persona);
        petList.appendChild(petCard);
      });

      // 펫 추가 버튼 생성
      const addButton = createPetAddButton();
      petList.appendChild(addButton);

      // 각 펫의 일기 수
      await loadPetDiaryCounts(data.personas);
    } else if (!data.success && data.message === "로그인이 필요합니다.") {
      alert("로그인 세션이 만료되었습니다. 다시 로그인해주세요.");
      window.location.href = "/login";
    } else {
      loadingMsg.innerHTML =
        '<p class="text-red-500">등록된 반려동물이 없습니다.</p>';
    }
  } catch (error) {
    console.error("펫 목록 로드 실패:", error);
    const loadingMsg = document.getElementById("petLoadingMsg");
    loadingMsg.innerHTML =
      '<p class="text-red-500">펫 목록을 불러오는데 실패했습니다.</p>';
  }
}

// "전체 일기" 버튼 생성
function createAllDiariesButton() {
  const div = document.createElement("div");
  div.className =
    "all-diaries-btn pet-card p-4 rounded-xl bg-gradient-to-r from-blue-100 to-indigo-100 hover:from-blue-200 hover:to-indigo-200 transition-all duration-300 cursor-pointer active";
  div.dataset.petPersonaId = "all";

  div.innerHTML = `
    <div class="flex items-center space-x-3">
      <div class="pet-emoji w-12 h-12 rounded-full bg-gradient-to-br from-blue-400 to-indigo-400 flex items-center justify-center text-white font-bold text-lg shadow-lg">
        📚
      </div>
      <div>
        <h3 class="font-semibold text-gray-800">전체 일기</h3>
        <p class="text-xs text-gray-600 diary-count">전체 일기 보기</p>
      </div>
    </div>
  `;

  div.addEventListener("click", function () {
    showAllDiaries();
  });

  return div;
}

// 전체 일기 표시 함수
async function showAllDiaries() {
  // 모든 펫 카드 비활성화
  document.querySelectorAll(".pet-card").forEach((card) => {
    card.classList.remove("active");
  });

  // "전체 일기" 버튼 활성화
  const allDiariesBtn = document.querySelector(".all-diaries-btn");
  if (allDiariesBtn) {
    allDiariesBtn.classList.add("active");
  }

  // 선택된 펫 정보 초기화
  selectedPetPersonaId = null;
  document.getElementById("selectedPetName").textContent = "전체 일기";
  document.getElementById("selectedPetInfo").style.display = "block";

  // 전체 일기 로드 (첫 페이지)
  await loadAllDiaries(1);
}

// 각 펫의 일기 수
async function loadPetDiaryCounts(personas) {
  for (const persona of personas) {
    try {
      const response = await fetch(
        `/api/diary/list/${persona.pet_persona_id}?page=1`
      );
      const data = await response.json();

      if (data.success) {
        updateDiaryCount(
          persona.pet_persona_id,
          data.pagination ? data.pagination.total_items : data.diaries.length
        );
      }
    } catch (error) {
      console.error(`펫 ${persona.pet_name}의 일기 수 로드 실패:`, error);
    }
  }
}

// 펫 카드 생성
function createPetCard(persona) {
  const div = document.createElement("div");
  div.className =
    "pet-card p-4 rounded-xl bg-gradient-to-r from-orange-100 to-yellow-100 hover:from-orange-200 hover:to-yellow-200 transition-all duration-300 cursor-pointer";
  div.dataset.petPersonaId = persona.pet_persona_id;

  // 종류에 따른 이모지 설정
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
    "pet-add-btn p-4 rounded-xl border-2 border-dashed border-gray-300 hover:border-orange-400 hover:bg-orange-50 transition-all duration-300 cursor-pointer";

  div.innerHTML = `
    <div class="flex items-center justify-center space-x-2 text-gray-500 hover:text-orange-600">
      <i class="fas fa-plus-circle text-2xl"></i>
      <span class="font-medium">펫 추가하기</span>
    </div>
  `;

  // 펫 등록 페이지로 이동
  div.addEventListener("click", function () {
    window.location.href = "/mypage";
  });

  return div;
}

// 펫 선택
async function selectPet(petPersonaId, petName) {
  try {
    // 모든 펫 카드 비활성화
    document.querySelectorAll(".pet-card").forEach((card) => {
      card.classList.remove("active");
    });

    // 선택된 펫 카드 활성화
    const selectedCard = document.querySelector(
      `[data-pet-persona-id="${petPersonaId}"]`
    );
    if (selectedCard) {
      selectedCard.classList.add("active");
    }

    // 선택된 펫 정보 업데이트
    selectedPetPersonaId = petPersonaId;
    document.getElementById("selectedPetName").textContent = petName;
    document.getElementById("selectedPetInfo").style.display = "block";

    console.log(`선택한 펫: ${petName} (ID: ${petPersonaId})`);

    // 해당 펫의 일기 목록 로드 (첫 페이지)
    await loadPetDiaries(petPersonaId, 1);
  } catch (error) {
    console.error("펫 선택 실패:", error);
    alert("펫 선택 중 오류가 발생했습니다.");
  }
}

// 특정 펫의 일기 목록 로드 (페이징 추가)
async function loadPetDiaries(petPersonaId, page = 1) {
  const tableBody = document.getElementById("diaryTableBody");

  try {
    // 로딩 표시
    tableBody.innerHTML = `
      <tr>
        <td colspan="4" class="text-center py-8 text-gray-500">
          <i class="fas fa-spinner fa-spin mr-2"></i>
          일기를 불러오는 중...
        </td>
      </tr>
    `;

    const response = await fetch(
      `/api/diary/list/${petPersonaId}?page=${page}`
    );
    const data = await response.json();

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    if (data.success && data.diaries.length > 0) {
      allDiaries = data.diaries;
      currentPage = data.pagination.current_page;
      totalPages = data.pagination.total_pages;

      displayDiaries(data.diaries);
      updatePagination(data.pagination, "pet", petPersonaId);

      // 일기 수 업데이트
      updateDiaryCount(petPersonaId, data.pagination.total_items);
    } else {
      tableBody.innerHTML = `
        <tr>
          <td colspan="4" class="empty-state text-center py-8">
            <i class="fas fa-book-open text-4xl text-gray-300 mb-4"></i>
            <p class="text-gray-500 font-medium">아직 작성된 일기가 없습니다.</p>
            <p class="text-sm text-gray-400 mt-2">첫 번째 일기를 작성해보세요!</p>
          </td>
        </tr>
      `;
      hidePagination();
    }
  } catch (error) {
    console.error("일기 목록 로드 실패:", error);
    tableBody.innerHTML = `
      <tr>
        <td colspan="4" class="text-center py-8 text-red-500">
          <i class="fas fa-exclamation-triangle mr-2"></i>
          일기 목록을 불러오는데 실패했습니다.
        </td>
      </tr>
    `;
    hidePagination();
  }
}

// 특정 펫의 일기 목록 표시 (펫 이름 없음)
function displayDiaries(diaries) {
  const tableBody = document.getElementById("diaryTableBody");

  if (!diaries || diaries.length === 0) {
    tableBody.innerHTML = `
      <tr>
        <td colspan="4" class="empty-state text-center py-8">
          <i class="fas fa-book-open text-4xl text-gray-300 mb-4"></i>
          <p class="text-gray-500 font-medium">일기가 없습니다.</p>
        </td>
      </tr>
    `;
    return;
  }

  tableBody.innerHTML = diaries
    .map(
      (diary, index) => `
        <tr class="diary-row border-b hover:bg-orange-50 transition-colors duration-200 cursor-pointer" onclick="viewDiaryDetail(${
          diary.diary_id
        })">
          <td class="py-4 px-4 text-gray-600">${
            (currentPage - 1) * 5 + index + 1
          }</td>
          <td class="py-4 px-4">
            <div class="flex items-center space-x-2">
              <span class="font-medium text-gray-800">${diary.title}</span>
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

// 페이지네이션 업데이트 (새로 추가)
function updatePagination(pagination, type, petId = null) {
  const paginationDiv = document.getElementById("pagination");

  if (pagination.total_pages <= 1) {
    hidePagination();
    return;
  }

  let paginationHTML = "";

  // 이전 페이지 버튼
  if (pagination.has_prev) {
    paginationHTML += `
      <button onclick="changePage(${
        pagination.current_page - 1
      }, '${type}', ${petId})" 
              class="px-3 py-1 rounded-lg bg-gray-200 text-gray-600 hover:bg-gray-300 transition-colors duration-200">
        <i class="fas fa-chevron-left"></i>
      </button>
    `;
  }

  // 페이지 번호 버튼들
  const startPage = Math.max(1, pagination.current_page - 2);
  const endPage = Math.min(pagination.total_pages, pagination.current_page + 2);

  for (let i = startPage; i <= endPage; i++) {
    const isActive = i === pagination.current_page;
    paginationHTML += `
      <button onclick="changePage(${i}, '${type}', ${petId})" 
              class="px-3 py-1 rounded-lg ${
                isActive
                  ? "bg-orange-400 text-white"
                  : "bg-gray-200 text-gray-600 hover:bg-gray-300"
              } transition-colors duration-200">
        ${i}
      </button>
    `;
  }

  // 다음 페이지 버튼
  if (pagination.has_next) {
    paginationHTML += `
      <button onclick="changePage(${
        pagination.current_page + 1
      }, '${type}', ${petId})" 
              class="px-3 py-1 rounded-lg bg-gray-200 text-gray-600 hover:bg-gray-300 transition-colors duration-200">
        <i class="fas fa-chevron-right"></i>
      </button>
    `;
  }

  paginationDiv.innerHTML = paginationHTML;
  paginationDiv.style.display = "flex";
}

// 페이지 변경 함수 (새로 추가)
function changePage(page, type, petId = null) {
  if (type === "all") {
    loadAllDiaries(page);
  } else if (type === "pet" && petId) {
    loadPetDiaries(petId, page);
  }
}

// 페이지네이션 숨기기 (새로 추가)
function hidePagination() {
  const pagination = document.getElementById("pagination");
  if (pagination) {
    pagination.style.display = "none";
  }
}

// 일기 상세보기 함수
function viewDiaryDetail(diaryId) {
  window.location.href = `/diary/detail/${diaryId}`;
}

// 일기 수 업데이트
function updateDiaryCount(petPersonaId, count) {
  const petCard = document.querySelector(
    `[data-pet-persona-id="${petPersonaId}"]`
  );
  if (petCard) {
    const countElement = petCard.querySelector(".diary-count");
    if (countElement) {
      countElement.textContent = `일기 ${count}개`;
    }
  }
}

// 일기 검색
function searchDiary() {
  const searchValue = document
    .getElementById("searchInput")
    .value.toLowerCase()
    .trim();

  if (searchValue === "") {
    // 현재 선택된 상태에 따라 표시
    if (selectedPetPersonaId) {
      displayDiaries(allDiaries);
    } else {
      displayAllDiaries(allDiaries);
    }
    return;
  }

  const filteredDiaries = allDiaries.filter(
    (diary) =>
      (diary.title && diary.title.toLowerCase().includes(searchValue)) ||
      (diary.content_user &&
        diary.content_user.toLowerCase().includes(searchValue)) ||
      (diary.content_ai &&
        diary.content_ai.toLowerCase().includes(searchValue)) ||
      (diary.pet_name && diary.pet_name.toLowerCase().includes(searchValue))
  );

  // 현재 선택된 상태에 따라 표시 방식 결정
  if (selectedPetPersonaId) {
    displayDiaries(filteredDiaries);
  } else {
    displayAllDiaries(filteredDiaries);
  }

  if (filteredDiaries.length === 0) {
    const tableBody = document.getElementById("diaryTableBody");
    tableBody.innerHTML = `
      <tr>
        <td colspan="4" class="empty-state text-center py-8">
          <i class="fas fa-search text-4xl text-gray-300 mb-4"></i>
          <p class="text-gray-500 font-medium">"${searchValue}"에 대한 검색 결과가 없습니다.</p>
          <p class="text-sm text-gray-400 mt-2">다른 키워드로 검색해보세요.</p>
        </td>
      </tr>
    `;
  }
}

// 날짜 포맷팅
function formatDate(dateString) {
  try {
    const date = new Date(dateString);
    if (isNaN(date.getTime())) {
      return "날짜 오류";
    }

    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, "0");
    const day = String(date.getDate()).padStart(2, "0");
    return `${year}-${month}-${day}`;
  } catch (error) {
    console.error("날짜 포맷팅 오류:", error);
    return "날짜 오류";
  }
}
