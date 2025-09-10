const pet_selector_btn = document.getElementById("pet-selector-btn");
const pet_dropdown_menu = document.getElementById("pet-dropdown-menu");
const dropdown_arrow = document.getElementById("dropdown-arrow");
const selected_pet_icon = document.getElementById("selected-pet-icon");
const selected_pet_name = document.getElementById("selected-pet-name");
const selected_pet_species = document.getElementById("selected-pet-species");
let current_pet_id = null;
let pets_data = [];

// 펫카드 드롭다운 기능
function initPetDropdown() {
  // 드롭다운 토글
  pet_selector_btn.addEventListener("click", function() {
    const isHidden = pet_dropdown_menu.classList.contains("hidden");
    if (isHidden) {
      pet_dropdown_menu.classList.remove("hidden");
      dropdown_arrow.style.transform = "rotate(180deg)";
    } else {
      pet_dropdown_menu.classList.add("hidden");
      dropdown_arrow.style.transform = "rotate(0deg)";
    }
  });

  // 외부 클릭 시 드롭다운 닫기
  document.addEventListener("click", function(e) {
    if (!pet_selector_btn.contains(e.target) && !pet_dropdown_menu.contains(e.target)) {
      pet_dropdown_menu.classList.add("hidden");
      dropdown_arrow.style.transform = "rotate(0deg)";
    }
  });
}

// 펫 선택 함수
function selectPet(pet) {
  // 선택된 펫 정보 업데이트
  selected_pet_icon.textContent = pet.icon;
  selected_pet_name.textContent = pet.pet_name;
  selected_pet_species.textContent = pet.species_name;
  
  // current_pet_id 설정
  current_pet_id = Number(pet.pet_id);
  localStorage.setItem("currentPetId", current_pet_id);
  
  // 드롭다운 닫기
  pet_dropdown_menu.classList.add("hidden");
  dropdown_arrow.style.transform = "rotate(0deg)";
  
  // 이벤트 발송
  window.dispatchEvent(new Event("petChanged"));
  
  if (current_pet_id) {
    getMedications(current_pet_id);
  }
}

// 전체 펫 조회
async function getAllPetsById() {
  try {
    const response = await fetch(`/api/dailycares/get-pet/`);
    if (!response.ok) throw new Error("Failed to fetch pet list");
    const pets = await response.json();
    console.log("회원의 petList입니다. ", pets);
    
    pets_data = pets;

    // 드롭다운 메뉴에 펫 옵션들 추가
    pet_dropdown_menu.innerHTML = "";
    
    pets.forEach((pet) => {
      // 동물 아이콘 결정
      let animalIcon = "🐾"; // 기본 아이콘
      if (pet.species_name) {
        if (
          pet.species_name.includes("강아지") ||
          pet.species_name.includes("개")
        ) {
          animalIcon = "🐶";
        } else if (
          pet.species_name.includes("고양이") ||
          pet.species_name.includes("cat")
        ) {
          animalIcon = "🐱";
        } else if (pet.species_name.includes("토끼")) {
          animalIcon = "🐰";
        } else if (
          pet.species_name.includes("새") ||
          pet.species_name.includes("조류")
        ) {
          animalIcon = "🐦";
        } else if (pet.species_name.includes("햄스터")) {
          animalIcon = "🐹";
        }
      }

      // 펫 옵션 생성
      const petOption = document.createElement("div");
      petOption.className = "pet-option p-3 hover:bg-gray-50 cursor-pointer transition-colors";
      petOption.innerHTML = `
        <div class="flex items-center space-x-3">
          <span class="text-2xl">${animalIcon}</span>
          <div>
            <div class="font-semibold text-gray-800">${pet.pet_name}</div>
            <div class="text-sm text-gray-500">${pet.species_name}</div>
          </div>
        </div>
      `;

      // 클릭 이벤트
      petOption.addEventListener("click", function() {
        selectPet({
          ...pet,
          icon: animalIcon
        });
      });

      pet_dropdown_menu.appendChild(petOption);
    });

    // 드롭다운 초기화
    initPetDropdown();

    // 🔹 페이지 로드 후, 이전에 선택한 pet 자동 선택
    const storedPetId = localStorage.getItem("currentPetId");
    if (storedPetId) {
      const storedPet = pets.find(p => p.pet_id == storedPetId);
      if (storedPet) {
        let animalIcon = "🐾";
        if (storedPet.species_name) {
          if (storedPet.species_name.includes("강아지") || storedPet.species_name.includes("개")) {
            animalIcon = "🐶";
          } else if (storedPet.species_name.includes("고양이") || storedPet.species_name.includes("cat")) {
            animalIcon = "🐱";
          } else if (storedPet.species_name.includes("토끼")) {
            animalIcon = "🐰";
          } else if (storedPet.species_name.includes("새") || storedPet.species_name.includes("조류")) {
            animalIcon = "🐦";
          } else if (storedPet.species_name.includes("햄스터")) {
            animalIcon = "🐹";
          }
        }
        selectPet({
          ...storedPet,
          icon: animalIcon
        });
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
    console.error("Pet 리스트를 불러올 수 없습니다:", error);
    selected_pet_name.textContent = "펫 정보를 불러올 수 없습니다";
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

    // 항상 JSON 응답 받기
    const result = await response.json();

    if (!result.success) {
      alert(result.message || "기록저장이 실패되었습니다.");
      return;
    }

    console.log("기록저장완료:", result.data);
    alert("건강기록이 저장되었습니다.");
    window.dispatchEvent(
      new CustomEvent("healthcareSaved", {
        detail: { pet_id: pet_id },
      })
    );
    resetHealthcareForm();
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

      // 우선순위에 따른 배지 스타일 결정
      const getPriorityStyle = (priority) => {
        switch(priority) {
          case "높음": return "bg-red-100 text-red-700 border border-red-300";
          case "보통": return "bg-yellow-100 text-yellow-700 border border-yellow-300";
          case "낮음": return "bg-green-100 text-green-700 border border-green-300";
          default: return "bg-gray-100 text-gray-700 border border-gray-300";
        }
      };

      // 상태에 따른 배지 스타일 결정
      const getStatusStyle = (status) => {
        if (status === "완료") {
          return "bg-green-100 text-green-700 border border-green-300";
        } else {
          return "bg-blue-100 text-blue-700 border border-blue-300";
        }
      };

      todoCard.innerHTML = `
        <div class="card-hover bg-gradient-to-br from-yellow-50 to-orange-50 rounded-xl p-6 border border-orange-200 shadow-sm hover:shadow-md transition-shadow">
          <!-- 헤더: 우선순위, 상태, 등록일 -->
          <div class="flex items-center justify-between mb-4 pb-3 border-b border-orange-100">
            <div class="flex items-center gap-2">
              <span class="px-2 py-1 rounded-full text-xs font-medium ${getPriorityStyle(e.priority)}">
                ${e.priority}
              </span>
              <span class="todo-status cursor-pointer hover:opacity-80 transition-opacity px-2 py-1 rounded-full text-xs font-medium ${getStatusStyle(e.status)}" 
                    data-id="${e.todo_id}">
                <i class="fas fa-${e.status === "완료" ? "check-circle" : "clock"} mr-1"></i>${e.status}
              </span>
            </div>
            <div class="text-sm text-gray-500 font-medium">
              ${e.created_at.slice(0, 10)}
            </div>
          </div>
          
          <!-- 메인 콘텐츠: 케어 제목과 세부 내용 중점 표시 -->
          <div class="todo-card cursor-pointer" onclick="clickCard(${e.todo_id})">
            <div class="mb-3">
              <h3 class="text-lg font-bold text-gray-800 mb-2 leading-tight">${e.title}</h3>
              <p class="text-gray-600 leading-relaxed">${e.description || "상세내용이 등록되지 않았습니다."}</p>
            </div>
          </div>
        </div>
      `;
      // 여기서 직접 이벤트 등록
      todoCard.querySelector(".todo-card").addEventListener("click", () => {
        window.location.href = `todo?todo_id=${e.todo_id}`;
      });

      resultDiv.appendChild(todoCard);
    });

 

    // 상태 변경 이벤트 리스너 (상태 클릭시)
    resultDiv.addEventListener("click", async (event) => {
      const statusTarget = event.target.closest(".todo-status");

      if (statusTarget) {
        const todoId = statusTarget.dataset.id;
        console.log("Status clicked - TODO ID", todoId);
      

        const currentStatus = statusTarget.textContent
          .trim()
          .replace(/.*\s/, ""); // 아이콘 제거하고 상태만 추출
        let newStatus;

        if (currentStatus === "완료") {
          newStatus = "미완료";
        } else {
          newStatus = "완료";
        }

        try {
          const response = await fetch(`/api/dailycares/todo/${todoId}`, {
            method: "PUT",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ status: newStatus }),
          });

          if (response.ok) {
            // 상태 변경 성공 시 UI 업데이트
            const icon = statusTarget.querySelector("i");
            statusTarget.innerHTML = `<i class="fas fa-${
              newStatus === "완료" ? "check-circle" : "clock"
            } mr-1"></i>${newStatus}`;

            // 스타일 업데이트
            if (newStatus === "완료") {
              statusTarget.className = statusTarget.className.replace(
                /bg-blue-100 text-blue-800 border-blue-300/,
                "bg-gray-100 text-gray-600 border-gray-300"
              );
            } else {
              statusTarget.className = statusTarget.className.replace(
                /bg-gray-100 text-gray-600 border-gray-300/,
                "bg-blue-100 text-blue-800 border-blue-300"
              );
            }

            console.log(`상태가 ${newStatus}로 변경되었습니다.`);
          } else {
            alert("상태 변경 실패");
          }
        } catch (err) {
          console.error("상태 변경 실패:", err);
          alert("네트워크 오류가 발생했습니다.");
        }
        return;
      }

    
    
    });
  } catch (err) {
    console.error("Todo 조회 실패:", err);
    alert("할일 목록을 불러오는데 실패했습니다.");
  }
}

// 리포트 기록 js 추가
function setWhiteBackground() {
  const healthWidget = document.querySelector(".health-report-widget");
  if (healthWidget) {
    healthWidget.style.background = "white";
    healthWidget.style.color = "#333";
    healthWidget.style.boxShadow = "0 8px 25px rgba(0, 0, 0, 0.15)";

    // 제목 색상 변경
    const title = healthWidget.querySelector("h3");
    if (title) {
      title.style.color = "#333";
    }

    // 버튼 스타일 변경
    const button = healthWidget.querySelector(".btn");
    if (button) {
      button.style.background = "linear-gradient(135deg, #667eea, #764ba2)";
      button.style.color = "white";
    }
  }
}

// 건강 요약 업데이트 함수 (흰색 배경 버전)
async function updateHealthWidget() {
  try {
    // 배경을 흰색으로 변경
    setWhiteBackground();

    const currentPetId = localStorage.getItem("currentPetId");
    if (!currentPetId) {
      updateWidgetContent("반려동물을 선택해주세요");
      return;
    }

    // 로딩 상태 표시
    updateWidgetContent("건강 데이터를 불러오는 중...");

    // 7일 데이터 가져오기
    const response = await fetch(
      `/api/dailycares/health-chart/${currentPetId}?days=7`
    );

    if (!response.ok) {
      throw new Error("데이터 요청 실패");
    }

    const chartData = await response.json();

    if (chartData.dates.length === 0) {
      updateWidgetContent("최근 건강 기록이 없습니다");
      return;
    }

    // 요약 데이터 생성
    const summary = generateHealthSummary(chartData);

    // 위젯 내용 업데이트
    updateWidgetContent(summary);
  } catch (error) {
    console.error("건강 요약 업데이트 실패:", error);
    updateWidgetContent("데이터를 불러올 수 없습니다");
  }
}

// 위젯 내용 업데이트 함수 (흰색 배경용)
function updateWidgetContent(content) {
  const healthScore = document.querySelector(".health-score");
  const healthText = document.querySelector(".health-report-widget p");

  if (typeof content === "string") {
    // 에러나 로딩 메시지인 경우
    if (healthScore) {
      healthScore.innerHTML = `
      <div style="
        text-align: center; 
        padding: 20px; 
        color: #666; 
        font-size: 0.9rem; 
        font-weight: 500;
        line-height: 1.4;
        background: rgba(0,0,0,0.02);
        border-radius: 8px;
        border: 1px solid rgba(0,0,0,0.05);
      ">
        ${content}
      </div>
    `;
    }
    if (healthText) healthText.textContent = "";
  } else {
    // 요약 데이터인 경우
    if (healthScore) {
      healthScore.innerHTML = `
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px; font-size: 0.8rem;">
          <div style="background: #fff5f5; padding: 8px; border-radius: 6px; border-left: 3px solid #ff6b6b; border: 1px solid #ffe3e3;">
            <div style="font-size: 0.7rem; color: #666; margin-bottom: 3px; font-weight: 600;">몸무게</div>
            <div style="font-weight: 700; margin-bottom: 2px; color: #333;">${content.weight.trend}</div>
            <div style="font-size: 0.65rem; color: #888;">${content.weight.average}</div>
          </div>
          <div style="background: #f0fdfc; padding: 8px; border-radius: 6px; border-left: 3px solid #4ecdc4; border: 1px solid #ccfbf1;">
            <div style="font-size: 0.7rem; color: #666; margin-bottom: 3px; font-weight: 600;">식사량</div>
            <div style="font-weight: 700; margin-bottom: 2px; color: #333;">${content.food.trend}</div>
            <div style="font-size: 0.65rem; color: #888;">${content.food.average}</div>
          </div>
          <div style="background: #f0f9ff; padding: 8px; border-radius: 6px; border-left: 3px solid #45aaf2; border: 1px solid #dbeafe;">
            <div style="font-size: 0.7rem; color: #666; margin-bottom: 3px; font-weight: 600;">수분섭취</div>
            <div style="font-weight: 700; margin-bottom: 2px; color: #333;">${content.water.trend}</div>
            <div style="font-size: 0.65rem; color: #888;">${content.water.average}</div>
          </div>
          <div style="background: #faf5ff; padding: 8px; border-radius: 6px; border-left: 3px solid #a55eea; border: 1px solid #e9d5ff;">
            <div style="font-size: 0.7rem; color: #666; margin-bottom: 3px; font-weight: 600;">활동량</div>
            <div style="font-weight: 700; margin-bottom: 2px; color: #333;">${content.exercise.trend}</div>
            <div style="font-size: 0.65rem; color: #888;">${content.exercise.average}</div>
          </div>
        </div>
      `;
    }

    if (healthText) {
      healthText.textContent = "최근 7일간의 건강 데이터 요약입니다";
      healthText.style.color = "#666";
      healthText.style.marginBottom = "16px";
    }
  }
}

// 건강 요약 데이터 생성
function generateHealthSummary(chartData) {
  const recentData = {
    weight: chartData.weight.slice(-7),
    food: chartData.food.slice(-7),
    water: chartData.water.slice(-7),
    exercise: chartData.exercise.slice(-7),
  };

  return {
    weight: analyzeWeightTrend(recentData.weight),
    food: analyzeFoodTrend(recentData.food),
    water: analyzeWaterTrend(recentData.water),
    exercise: analyzeExerciseTrend(recentData.exercise),
  };
}

// 트렌드 분석 함수들 (기존 analysis.js에서 가져옴)
function analyzeWeightTrend(weights) {
  if (weights.length < 2) return { trend: "데이터 부족", average: "" };

  const first = weights[0];
  const last = weights[weights.length - 1];
  const change = last - first;
  const avg = (weights.reduce((a, b) => a + b, 0) / weights.length).toFixed(1);

  let trendText = "";
  if (Math.abs(change) < 0.1) {
    trendText = "안정적 유지";
  } else if (change > 0) {
    trendText = `${change.toFixed(1)}kg 증가`;
  } else {
    trendText = `${Math.abs(change).toFixed(1)}kg 감소`;
  }

  return {
    trend: trendText,
    average: `평균 ${avg}kg`,
  };
}

function analyzeFoodTrend(foods) {
  if (foods.length < 2) return { trend: "데이터 부족", average: "" };

  const avg = (foods.reduce((a, b) => a + b, 0) / foods.length).toFixed(0);
  const first = foods[0];
  const last = foods[foods.length - 1];
  const overallChange = ((last - first) / first) * 100;

  let trendText = "";
  if (Math.abs(overallChange) < 15) {
    trendText = "일정한 섭취";
  } else if (overallChange > 0) {
    trendText = `섭취량 증가 (+${overallChange.toFixed(0)}%)`;
  } else {
    trendText = `섭취량 감소 (${Math.abs(overallChange).toFixed(0)}%)`;
  }

  return {
    trend: trendText,
    average: `평균 ${avg}g`,
  };
}

function analyzeWaterTrend(waters) {
  if (waters.length < 2) return { trend: "데이터 부족", average: "" };

  const avg = (waters.reduce((a, b) => a + b, 0) / waters.length).toFixed(0);
  const first = waters[0];
  const last = waters[waters.length - 1];
  const overallChange = ((last - first) / first) * 100;

  let trendText = "";
  if (Math.abs(overallChange) < 20) {
    trendText = "일정한 수준";
  } else if (overallChange > 0) {
    trendText = `섭취량 증가 (+${overallChange.toFixed(0)}%)`;
  } else {
    trendText = `섭취량 감소 (${Math.abs(overallChange).toFixed(0)}%)`;
  }

  return {
    trend: trendText,
    average: `평균 ${avg}ml`,
  };
}

function analyzeExerciseTrend(exercises) {
  if (exercises.length < 2) return { trend: "데이터 부족", average: "" };

  const avg = (exercises.reduce((a, b) => a + b, 0) / exercises.length).toFixed(
    0
  );
  const first = exercises[0];
  const last = exercises[exercises.length - 1];
  const change = last - first;

  let trendText = "";
  if (Math.abs(change) < 10) {
    trendText = "일정한 활동량";
  } else if (change > 0) {
    trendText = `활동량 증가 (+${change.toFixed(0)}분)`;
  } else {
    trendText = `활동량 감소 (${Math.abs(change).toFixed(0)}분)`;
  }

  return {
    trend: trendText,
    average: `평균 ${avg}분`,
  };
}

// 이벤트 리스너 추가
window.addEventListener("petChanged", function () {
  updateHealthWidget();
});

window.addEventListener("healthcareSaved", function (event) {
  // 건강 기록 저장 후 1초 뒤 업데이트
  setTimeout(() => {
    updateHealthWidget();
  }, 1000);
});

// 페이지 로드시 실행 (기존 DOMContentLoaded에 추가)
document.addEventListener("DOMContentLoaded", function () {
  // 기존 코드들...

  // 건강 요약 위젯 업데이트
  setTimeout(() => {
    updateHealthWidget();
  }, 500); // 다른 초기화가 완료된 후 실행
});

document.addEventListener("DOMContentLoaded", () => {
  getTodo();
  getAllPetsById();
});
