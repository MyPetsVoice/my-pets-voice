const pet_selector = document.getElementById("pet-selector");
const pet_detail = document.getElementById("pet-detail");
let current_pet_id = null;

// 전체 펫 조회
async function getAllPetsById() {
  try {
    const response = await fetch(`/api/dailycares/get-pet/`);
    if (!response.ok) throw new Error("Failed to fetch pet list");
    const pets = await response.json();
    console.log("회원의 petList입니다. ", pets);

    // pet-card 생성 (전체 pet)
    pets.forEach((pet) => {
      const card = document.createElement("div");
      card.className = "pet-card";
      card.dataset.petId = pet.pet_id;
      card.innerHTML = `<strong>${pet.pet_name}</strong><small>${pet.species_name}</small>`;
      pet_selector.appendChild(card);

      // 클릭 이벤트 (개별 pet 정보)
      card.addEventListener("click", async function () {
        // active 표시
        pet_selector
          .querySelectorAll(".pet-card")
          .forEach((c) => c.classList.remove("active"));
        this.classList.add("active");

        // 현재 선택된 pet_id 숫자로 변환
        current_pet_id = Number(this.dataset.petId);

        

        // 🔹 localStorage 에 저장
        localStorage.setItem("currentPetId", current_pet_id);

        window.dispatchEvent(new Event("petChanged"));


        if(current_pet_id){
            const response = await fetch(
            `/api/dailycares/get-pet/${current_pet_id}`
          );
          if (!response.ok) {
            pet_detail.innerHTML = "<p>Pet 정보를 불러올 수 없습니다.</p>";
            return;
          }
          const petData = await response.json();
          console.log("선택된 pet 데이터:", petData);
          getMedications(current_pet_id);

          pet_detail.innerHTML = `
            <h3>${petData.pet_name} (${petData.species_name})</h3>
            <p>종: ${petData.breed_name}</p>
            <p>나이: ${petData.pet_age}</p>
            <p>성별: ${petData.pet_gender}</p>
            <p>중성화 여부: ${petData.is_neutered ? "Yes" : "No"}</p>
          `;
        } else {
          
          pet_detail.innerHTML =
            "<p>Pet 정보를 불러오는 중 오류가 발생했습니다.</p>";
        }
      });
    });

    // 🔹 페이지 로드 후, 이전에 선택한 pet 자동 선택
    const storedPetId = localStorage.getItem("currentPetId");
    if (storedPetId) {
      const card = pet_selector.querySelector(
        `.pet-card[data-pet-id="${storedPetId}"]`
      );
      if (card) {
        card.click(); // 클릭 이벤트 강제로 실행해서 데이터 불러오기
      }
    }

    const historyBtn = document.getElementById("link_healthcare_history");
    historyBtn.addEventListener("click", () => {
      if (!current_pet_id || current_pet_id < 0) {
        alert("펫을 선택해주세요");
        return;
      }
      // 여기서는 이미 localStorage 저장됨 (중복 저장은 괜찮음)
      console.log(localStorage.getItem("currentPetId"));
      window.location.href = `/dailycare/health-history`;
    });
  } catch (error) {
    pet_selector.innerHTML = "<p>Pet 리스트를 불러올 수 없습니다.</p>";
  }
}

// 페이지 로딩 시 실행

var medicationSelect = document.getElementById("medication-select");
var selectedTags = document.getElementById("selected-tags");

// 선택된 약물 정보 저장 배열
let selectedItems = [];

// 약물 목록 불러오기 (디버깅 강화)
async function getMedications(pet_id) {
  console.log("🔄 getMedications 호출됨, pet_id:", pet_id);

  try {
    const response = await fetch(`/api/dailycares/medications/${pet_id}`);
    console.log("📡 API 응답 상태:", response.status);

    if (!response.ok) {
      throw new Error("영양제 목록을 불러오는데 실패했습니다.");
    }
    const data = await response.json();
    console.log("📋 받은 약물 데이터:", data);

    medicationSelect.innerHTML = '<option value="">약물을 선택하세요</option>';

    if (data.length > 0) {
      data.forEach((med) => {
        const option = document.createElement("option");
        option.value = med.medication_id;
        option.textContent = med.medication_name;
        medicationSelect.appendChild(option);
      });
      console.log("✅ 총", data.length, "개의 약물 옵션이 추가됨");
    } else {
      console.log("⚠️ 약/영양제 정보가 존재하지 않습니다.");
      const option = document.createElement("option");
      option.textContent =
        "약/영양제 정보가 없습니다. 약/영양제를 추가해주세요";
      option.disabled = true;
      medicationSelect.appendChild(option);
    }
  } catch (error) {
    console.error("❌ 약물 목록 로드 실패:", error);
  }
}

// 페이지 로드 시 자동 호출 (테스트용)
document.addEventListener("DOMContentLoaded", function () {
  console.log("📄 페이지 로드 완료");

  // current_pet_id가 있다면 자동으로 약물 목록 로드
  if (typeof current_pet_id !== "undefined" && current_pet_id) {
    console.log("🐕 자동으로 약물 목록 로드, pet_id:", current_pet_id);
    getMedications(current_pet_id);
  } else {
    console.log("⚠️ current_pet_id가 정의되지 않음");
  }
});

// 약물 선택 이벤트
medicationSelect.addEventListener("change", () => {
  const selectedValue = medicationSelect.value;
  const selectedText =
    medicationSelect.options[medicationSelect.selectedIndex].textContent;

  // 값이 있고 중복이 아닌 경우만 추가
  if (
    selectedValue &&
    !selectedItems.some((item) => item.value === selectedValue)
  ) {
    selectedItems.push({
      value: selectedValue,
      text: selectedText,
    });
    renderTags();
  }

  // 선택 초기화
  medicationSelect.value = "";
});

// 태그 렌더링
function renderTags() {
  selectedTags.innerHTML = "";

  selectedItems.forEach((item) => {
    const tag = document.createElement("span");
    tag.className =
      "flex items-center bg-yellow-100 text-yellow-800 px-3 py-1 rounded-full text-sm font-medium";

    tag.innerHTML = `
      ${item.text}
      <button type="button" 
        class="ml-2 text-yellow-600 hover:text-yellow-800 focus:outline-none remove-tag" 
        data-value="${item.value}">
        ✕
      </button>
    `;

    selectedTags.appendChild(tag);
  });
}

// 태그 삭제
selectedTags.addEventListener("click", (e) => {
  if (e.target.classList.contains("remove-tag")) {
    const valueToRemove = e.target.getAttribute("data-value");
    selectedItems = selectedItems.filter(
      (item) => item.value !== valueToRemove
    );
    renderTags();
  }
});

// 저장 버튼
document
  .getElementById("save_healthcare")
  .addEventListener("click", async () => {
    if (!confirm("오늘의 건강기록을 저장하시겠습니까?")) {
      return;
    }
    await saveHealthcare(current_pet_id);
  });

// 건강 기록 저장
async function saveHealthcare(pet_id) {
  const activePet = document.querySelector(".pet-card.active");
  if (!activePet) {
    alert("pet을 선택해주세요");
    return;
  }
  // ✅ 렌더된 태그에서 value 직접 가져오기
  const tagButtons = selectedTags.querySelectorAll("button[data-value]");
  const medication_ids = Array.from(tagButtons).map((btn) =>
    parseInt(btn.getAttribute("data-value"), 10)
  );

  console.log(medication_ids);

  const send_data = {
    pet_id: pet_id,
    food: document.getElementById("food-input").value,
    water: document.getElementById("water-input").value,
    excrement_status: document.getElementById("poop-select").value,
    weight_kg: document.getElementById("weight-input").value,
    walk_time_minutes: document.getElementById("walk-input").value,
    medication_ids: medication_ids,
  };

  console.log("📤 최종 저장할 정보:", send_data);

  try {
    const response = await fetch(`/api/dailycares/save/healthcare/${pet_id}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(send_data),
    });

    if (!response.ok) {
      const errorData = await response.json();
      alert(errorData.message || "기록저장이 실패되었습니다.");
    } else {
      console.log("기록저장완료");
      alert("건강기록이 저장되었습니다.");
      resetHealthcareForm();
    }
  } catch (error) {
    console.error("저장 실패:", error);
    alert("저장 중 오류가 발생했습니다.");
  }
}

// 폼 리셋
function resetHealthcareForm() {
  document.getElementById("food-input").value = "";
  document.getElementById("water-input").value = "";
  document.getElementById("poop-select").value = "";
  document.getElementById("weight-input").value = "";
  document.getElementById("walk-input").value = "";

  selectedItems = [];
  renderTags();
}

async function getTodo() {
  try {
    const response = await fetch(`/api/dailycares/todo/`);
    const todos = await response.json();
    console.log("todo data", todos);

    const resultDiv = document.getElementById("todo_div");
    if (!resultDiv) return;
    resultDiv.innerHTML = ""; // 초기화

    todos.forEach((e) => {
      const todoCard = document.createElement("div");

      todoCard.innerHTML = `
        <div class="card-hover bg-gradient-to-br from-yellow-50 to-orange-50 rounded-xl p-6 border border-yellow-200">
          <!-- Header -->
          <div class="flex items-center mb-4">
            <div class="bg-yellow-100 p-3 rounded-full">
              <span class="text-2xl">📝</span>
            </div>
            <div class="ml-3">
              <h3 class="font-semibold text-gray-800">${e.title}</h3>
              <p class="text-sm text-gray-600">${e.description || ""}</p>
            </div>
          </div>
          
          <!-- Record Details -->
          <div class="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
            <div class="text-center">
              <div class="text-2xl font-bold text-gray-800">${e.priority}</div>
              <div class="text-sm text-gray-600">우선순위</div>
            </div>
            <div class="text-center">
              <div class="text-2xl font-bold text-gray-800">${e.status}</div>
              <div class="text-sm text-gray-600">상태</div>
            </div>
            <div class="text-center">
              <div class="text-2xl font-bold text-gray-800">${e.created_at.slice(
                0,
                10
              )}</div>
              <div class="text-sm text-gray-600">등록일</div>
            </div>
            <div class="text-center">
              <div class="text-2xl font-bold text-gray-800">${e.updated_at.slice(
                0,
                10
              )}</div>
              <div class="text-sm text-gray-600">수정일</div>
            </div>
          </div>
          
          <!-- Footer -->
          <div class="pt-4 border-t border-yellow-200">
            <div class="flex justify-between items-center mb-2">
       <span class="text-sm text-gray-500">할일 상태</span>
      <span class="todo-status bg-green-100 text-green-800 px-3 py-1 rounded-full text-sm font-medium" data-id="${
        e.todo_id
      }">
        <i class="fas fa-check-circle mr-1"></i>${e.status}
      </span>
    </div>
              </div>
            </div>
          `;

      resultDiv.appendChild(todoCard);
    });

    resultDiv.addEventListener("click", async (event) => {
      const target = event.target.closest(".todo-status"); // 클릭한 요소가 상태 span인지 확인
      if (!target) return;

      const todoId = target.dataset.id;
      console.log("TODO ID", todoId);
      let newStatus;
      if (target.textContent.trim() === "완료") {
        newStatus = "미완료";
      } else {
        newStatus = "완료";
      }

      try {
        const response = await fetch(`/api/dailycares/todo/${todoId}`, {
          method: "PUT", // PUT 또는 PATCH
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ status: newStatus }),
        });

        if (response.ok) {
          target.textContent = newStatus; // 화면 업데이트
          alert("상태가 변경되었습니다.");
          getTodo();
          if (newStatus === "완료") {
            target.classList.remove("bg-green-100", "text-green-800");
            target.classList.add("bg-gray-200", "text-gray-600"); // 완료된 스타일 변경
          } else {
            target.classList.remove("bg-gray-200", "text-gray-600");
            target.classList.add("bg-green-100", "text-green-800"); // 미완료된 스타일 복구
          }
        } else {
          alert("상태 변경 실패");
        }
      } catch (err) {
        console.error("상태 변경 실패:", err);
      }
    });
  } catch (err) {
    console.error("Todo 조회 실패:", err);
  }
}

document.addEventListener("DOMContentLoaded", () => {
  getTodo();
  getAllPetsById();
});
