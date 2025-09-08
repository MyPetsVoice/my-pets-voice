document.addEventListener("DOMContentLoaded", () => {
  const careElement = document.getElementById("careElement");
  const careId = careElement.getAttribute("data-care-id");
  console.log("careId:", careId);

  if (!careId) {
    alert("care_id가 없습니다.");
    return;
  }

  const form = document.getElementById("editHealthForm");

  // 기존 기록 + 복용약 불러오기
  getHealthcare(careId, form);

  // 수정 버튼
  document.getElementById("submit").addEventListener("click", (e) => {
    e.preventDefault();
    updateHealthcare(careId, form);
  });

  // 삭제 버튼
  document.getElementById("deleteRecord").addEventListener("click", () => {
    deleteHealthcare(careId);
  });
});

// =============================
// 기존 기록 불러오기
// =============================
async function getHealthcare(care_id, form) {
  const response = await fetch(`/api/dailycares/get-healthcare/${care_id}`);
  if (!response.ok) {
    alert("기록 불러오기 실패");
    return;
  }

  const data = await response.json();
  console.log("기존 기록:", data);

  // 기본 필드 값 반영
  form.weight_kg.value = data.weight_kg || "";
  form.water.value = data.water || "";
  form.food.value = data.food || "";
  form.walk_time_minutes.value = data.walk_time_minutes || "";
  form.excrement_status.value = data.excrement_status || "";

  // 약물 옵션 목록 불러오기
  if (data.pet_id) {
    await loadMedications(data.pet_id);
  }

  // ✅ 기존 선택된 약물 반영
  if (data.medications && data.medications.length > 0) {
    selectedItems.length = 0; // 초기화
    data.medications.forEach((m) => {
      selectedItems.push({
        id: m.medication_id, // ← DB에서 넘어오는 키 확인 필요
        name: m.name,
      });
    });

    console.log("기존 선택된 약물:", selectedItems);
    renderSelectedMedications();
  }
}

// =============================
// 수정 제출
// =============================
async function updateHealthcare(care_id, form) {
  const payload = {
    weight_kg: form.weight_kg.value,
    water: form.water.value,
    food: form.food.value,
    walk_time_minutes: form.walk_time_minutes.value,
    excrement_status: form.excrement_status.value,
    medication_ids: selectedItems.map((item) => item.id), // 선택된 약물 ID 배열
  };

  console.log("제출 payload:", payload);

  const response = await fetch(`/api/dailycares/update/healthcare/${care_id}`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });

  if (response.ok) {
    alert("수정 완료!");
    window.location.href = `/dailycare/health-history?care_id=${care_id}`;
  } else {
    alert("수정 실패");
  }
}

// =============================
// 삭제
// =============================
async function deleteHealthcare(care_id) {
  const response = await fetch(`/api/dailycares/delete/healthcare/${care_id}`, {
    method: "DELETE",
  });

  if (response.ok) {
    alert("삭제 완료!");
    window.location.href = "/dailycare/health-history";
  } else {
    alert("삭제 실패");
  }
}

// =============================
// 약물 옵션 불러오기
// =============================
async function loadMedications(pet_id) {
  const response = await fetch(`/api/dailycares/medications/${pet_id}`);
  if (!response.ok) {
    console.error("약물 목록 불러오기 실패");
    return;
  }

  const medications = await response.json();
  console.log("약물 목록:", medications);

  const select = document.getElementById("medication-select");
  select.innerHTML = '<option value="">약물을 선택하세요</option>';

  medications.forEach((m) => {
    const option = document.createElement("option");
    option.value = m.medication_id;
    option.textContent = m.medication_name;
    select.appendChild(option);
  });
}

// =============================
// 선택/삭제 UI
// =============================
const selectedItems = [];

function renderSelectedMedications() {
  const container = document.getElementById("selectedMedications");
  container.innerHTML = "";

  if (selectedItems.length === 0) {
    container.innerHTML = `<p class="text-gray-400">선택된 약물이 없습니다.</p>`;
    return;
  }

  selectedItems.forEach((item) => {
    const div = document.createElement("div");
    div.className = "flex justify-between items-center bg-gray-100 p-2 rounded";

    div.innerHTML = `
      <span>${item.name}</span>
      <button type="button" class="text-red-500">❌</button>
    `;

    // 삭제 이벤트 등록
    div.querySelector("button").addEventListener("click", () => {
      const index = selectedItems.findIndex((i) => i.id === item.id);
      if (index > -1) {
        selectedItems.splice(index, 1);
        renderSelectedMedications();
      }
    });

    container.appendChild(div);
  });
}

// =============================
// 선택 이벤트 (드롭다운에서 선택 시 추가)
// =============================
document.getElementById("medication-select").addEventListener("change", (e) => {
  const id = parseInt(e.target.value);
  const name = e.target.options[e.target.selectedIndex].text;

  if (!id) return;

  if (selectedItems.some((i) => i.id === id)) {
    alert("이미 선택된 약물입니다.");
    return;
  }

  selectedItems.push({ id, name });
  renderSelectedMedications();
});
