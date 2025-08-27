document.addEventListener("DOMContentLoaded", () => {
  const careElement = document.getElementById("careElement");
  const careId = careElement.getAttribute("data-care-id");
  console.log(careId);
  if (!careId) {
    alert("care_id가 없습니다.");
    return;
  }

  const form = document.getElementById("editHealthForm"); // form 요소 선택

  getHealthcare(careId, form);

  document.getElementById("submit").addEventListener("click", (e) => {
    e.preventDefault(); // 폼 제출 막기
    updateHealthcare(careId, form);
  });

  document.getElementById("deleteRecord").addEventListener("click", () => {
    deleteHealthcare(careId);
  });
});

// 기존 기록 불러오기
async function getHealthcare(care_id, form) {
  const response = await fetch(`/api/dailycares/healthcare/${care_id}`);
  const data = await response.json();

  form.weight_kg.value = data.weight_kg;
  form.water.value = data.water;
  form.food.value = data.food;
  form.walk_time_minutes.value = data.walk_time_minutes;
  form.excrement_status.value = data.excrement_status;
}

// 수정 제출
async function updateHealthcare(care_id, form) {
  const payload = {
    weight_kg: form.weight_kg.value,
    water: form.water.value,
    food: form.food.value,
    walk_time_minutes: form.walk_time_minutes.value,
    excrement_status: form.excrement_status.value,
  };

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

// 삭제
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
