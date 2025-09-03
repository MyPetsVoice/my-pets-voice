const user_id = 1;
export let pet_id;
const pet_selector = document.getElementById("pet-selector");
const pet_detail = document.getElementById("pet-detail");
let current_pet_id = null;

// 펫 상세 정보를 가져와 화면에 표시
async function showPetDetail(petId) {
  try {
    const res = await fetch(`/api/dailycares/get-pet/${user_id}/${petId}`);
    if (!res.ok) throw new Error("Pet 정보를 불러올 수 없습니다.");
    const petData = await res.json();
    console.log("선택된 pet 데이터:", petData);

    // 약/영양제 가져오기
    getMedications(petId);

    pet_detail.innerHTML = `
      <h3>${petData.pet_name} (${petData.species_name})</h3>
      <p>종: ${petData.breed_name}</p>
      <p>나이: ${petData.pet_age}</p>
      <p>성별: ${petData.pet_gender}</p>
      <p>중성화 여부: ${petData.is_neutered ? "Yes" : "No"}</p>
    `;
  } catch (err) {
    console.error(err);
    pet_detail.innerHTML = "<p>Pet 정보를 불러오는 중 오류가 발생했습니다.</p>";
  }
}

// 펫 선택 처리
function selectPet(petId, cardElement) {
  // active 표시
  pet_selector
    .querySelectorAll(".pet-card")
    .forEach((c) => c.classList.remove("active"));
  cardElement.classList.add("active");

  current_pet_id = Number(petId);
  pet_id = current_pet_id;
  localStorage.setItem("currentPetId", current_pet_id);

  // 이벤트 발생 (다른 파일에서 처리 가능)
  window.dispatchEvent(
    new CustomEvent("petChanged", { detail: current_pet_id })
  );

  showPetDetail(current_pet_id);
}

// 전체 펫 조회 및 렌더링
async function getAllPetsById(user_id) {
  try {
    const res = await fetch(`/api/dailycares/get-pet/${user_id}`);
    if (!res.ok) throw new Error("Failed to fetch pet list");
    const pets = await res.json();
    console.log("회원의 petList입니다. ", pets);

    pet_selector.innerHTML = ""; // 초기화
    pets.forEach((pet) => {
      const card = document.createElement("div");
      card.className = "pet-card";
      card.dataset.petId = pet.pet_id;
      card.innerHTML = `<strong>${pet.pet_name}</strong><small>${pet.species_name}</small>`;
      card.addEventListener("click", () => selectPet(pet.pet_id, card));
      pet_selector.appendChild(card);
    });

    // 이전에 선택된 펫 유지
    const storedPetId = localStorage.getItem("currentPetId");
    if (storedPetId) {
      const card = pet_selector.querySelector(
        `.pet-card[data-pet-id="${storedPetId}"]`
      );
      if (card) selectPet(storedPetId, card);
    }
  } catch (err) {
    console.error(err);
    pet_selector.innerHTML = "<p>Pet 리스트를 불러올 수 없습니다.</p>";
  }
}

// 링크 버튼 처리
document
  .getElementById("link_healthcare_history")
  ?.addEventListener("click", () => {
    if (!current_pet_id) return alert("펫을 선택해주세요");
    localStorage.setItem("currentPetId", current_pet_id);
    window.location.href = `/dailycare/health-history`;
  });

// 초기 실행
getAllPetsById(user_id);

//
const medicationSelect = document.getElementById("medication-select");
// pet에 medication정보 불러오기
async function getMedications(pet_id) {
  const response = await fetch(`/api/dailycares/medications/${pet_id}`);
  if (!response.ok) {
    throw new Error("영양제 목록을 불러오는데 실패했습니다.");
  }
  const data = await response.json();
  console.log(data);

  medicationSelect.innerHTML = "";
  if (data.length > 0) {
    data.forEach((med) => {
      const option = document.createElement("option");
      option.value = med.medication_id;
      option.textContent = med.medication_name;
      medicationSelect.appendChild(option);
    });
  } else {
    console.log("약/영양제 정보가 존재하지 않습니다.");
    const option = document.createElement("option");
    option.textContent = "약/영양제 정보가 없습니다. 약/영양제를 추가해주세요";
    option.style.disabled = true;
    medicationSelect.appendChild(option);
  }
} // end getMedications(pet_id)

document
  .getElementById("save_healthcare")
  .addEventListener("click", async () => {
    if (!confirm("오늘의 건강기록을 저장하시겠습니까?")) {
      return;
    }
    await saveHealthcare(current_pet_id);
  });

async function saveHealthcare(pet_id) {
  const activePet = document.querySelector(".pet-card.active");
  if (!activePet) {
    alert("pet을 선택해주세요");
  }
  console.log(`현재 pet_id ${pet_id}`);
  console.log("save 중입니다.");
  const send_data = {
    pet_id: pet_id,
    food: document.getElementById("food-input").value,
    water: document.getElementById("water-input").value,
    excrement_status: document.getElementById("poop-select").value,
    weight_kg: document.getElementById("weight-input").value,
    walk_time_minutes: document.getElementById("walk-input").value,
    medication_ids: Array.from(medicationSelect.selectedOptions)
      .map((opt) => parseInt(opt.value))
      .filter((id) => !isNaN(id)),
  };

  console.log("저장할 정보입니다 : ", send_data);

  const response = await fetch(`/api/dailycares/save/healthcare/${pet_id}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(send_data),
  });

  if (!response.ok) {
    const errorData = await response.json()
    alert( errorData.message ||"기록저장이 실패되었습니다.");
  } else {
    console.log("기록저장완료");
    alert('건강기록이 저장되었습니다.')
  }
  resetHealthcareForm();
} // end saveHealthCares

function resetHealthcareForm() {
  document.getElementById("food-input").value = "";
  document.getElementById("water-input").value = "";
  document.getElementById("poop-select").selectedIndex = 0;
  document.getElementById("weight-input").value = "";
  document.getElementById("walk-input").value = "";

  // 다중 선택 select 초기화
  const medicationSelect = document.getElementById("medication-select");
  Array.from(medicationSelect.options).forEach(
    (option) => (option.selected = false)
  );
}

async function getTodo(user_id) {
  try {
    const response = await fetch(`/api/dailycares/todo/${user_id}`);
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
          getTodo(user_id);
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

getTodo(user_id);
