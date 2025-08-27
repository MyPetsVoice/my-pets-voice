// 공용 모달 열기: 각 health-item 클릭 시 모달 열기
document.querySelectorAll(".health-item.mdc").forEach((item) => {
  item.addEventListener("click", () => {
    const name = item.dataset.modal; // 모달 종류
    if (!current_pet_id) {
      alert("펫을 먼저 선택해주세요.");
      return;
    }
    openModal(name, current_pet_id); // 모달 열기
  });
});

// 모달 열기 함수
function openModal(name, pet_id) {
  console.log(`##### name ${name}, pet_id ${pet_id}`);
  fetch(`/api/dailycares/modal/${name}?pet_id=${pet_id}`)
    .then((res) => {
      if (!res.ok) throw new Error("네트워크 오류");
      return res.text();
    })
    .then((html) => {
      const modal = document.getElementById("common-modal");
      const content = modal.querySelector("#modalContent");

      // 서버에서 받은 HTML 삽입
      content.innerHTML = html;
      modal.classList.remove("hidden");

      // 닫기 버튼 이벤트
      const closeBtn = document.getElementById("modal-close-btn");
      closeBtn.onclick = () => modal.classList.add("hidden");

      // ---- 여기서 모달 내부 요소 접근 ----
      const hiddenInput = document.getElementById("modal-pet-id");
      const currentPetId = hiddenInput ? Number(hiddenInput.value) : pet_id;

      // 저장 버튼 이벤트 등록 (중복 방지 위해 먼저 초기화)
      const saveBtn = document.getElementById("save_medication_button");
      if (saveBtn) {
        saveBtn.onclick = () => {
          console.log("click button");
          saveMedication(currentPetId);
        };
      }
    })
    .catch((err) => {
      console.error("모달 불러오기 실패:", err);
      alert("모달을 불러오지 못했습니다.");
    });
}

// 모달 닫기 함수
function closeModal() {
  document.getElementById("common-modal").classList.add("hidden");
  location.reload(); 
}

// 저장 함수
async function saveMedication(pet_id) {
  console.log("saveMedication pet_id:", pet_id);
  const send_data = {
    pet_id: pet_id,
    medication_name: document.getElementById("medication_name_input").value,
    purpose: document.getElementById("purpose_input").value,
    dosage: document.getElementById("dosage_input").value,
    frequency: document.getElementById("frequency_option").value,
    start_date: document.getElementById("start_date_input").value,
    end_date: document.getElementById("end_date_input").value,
    side_effects_notes:
      document.getElementById("side_effects_notes_input").value || null,
    hospital_name: document.getElementById("hospital_name_input").value || null,
  };

  const response = await fetch(`/api/dailycares/save/medication/${pet_id}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(send_data),
  });

  if (!response.ok) {
    alert("기록 저장에 실패했습니다.");
  } else {
    console.log("기록 저장 완료");
    closeModal();
  }
}


// 여기서부터