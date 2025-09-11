// 의료 기록 설정
const medicalConfigs = {
  allergy: {
    endpoint: "/save/allergy/",
    fields: {
      allergy_type: "allergy_type_select",
      allergen: "allergen_input",
      symptoms: "symptoms_input",
      severity: "severity_select",
    },
    required: ["allergy_type", "allergen", "severity"],
    title: "알러지 정보",
  },

  disease: {
    endpoint: "/save/disease/",
    fields: {
      disease_name: "disease_name_input",
      symptoms: "symptoms_input",
      treatment_details: "treatment_details_input",
      hospital_name: "hospital_name_input",
      doctor_name: "doctor_name_input",
      medical_cost: "medical_cost_input",
      diagnosis_date: "diagnosis_date_input",
    },
    required: ["disease_name"],
    title: "질병 이력",
  },

  surgery: {
    endpoint: "/save/surgery/",
    fields: {
      surgery_name: "surgery_name_input",
      surgery_date: "surgery_date_input",
      surgery_summary: "surgery_summary_input",
      hospital_name: "hospital_name_input",
      doctor_name: "doctor_name_input",
      recovery_status: "recovery_status_select",
    },
    required: ["surgery_name", "surgery_date", "recovery_status"],
    title: "수술 이력",
  },

  vaccination: {
    endpoint: "/save/vaccination/",
    fields: {
      vaccine_name: "vaccine_name_input",
      vaccination_date: "vaccination_date_input",
      side_effects: "side_effects_input",
      hospital_name: "hospital_name_input",
      next_vaccination_date: "next_vaccination_date_input",
      manufacturer: "manufacturer_input", // 제조회사 추가
      lot_number: "lot_number_input", // 로트번호 추가
    },
    required: ["vaccine_name", "vaccination_date"],
    title: "예방접종 기록",
  },

  medication: {
    endpoint: "/save/medication/",
    fields: {
      medication_name: "medication_name_input",
      purpose: "purpose_input",
      dosage: "dosage_input",
      frequency: "frequency_select",
      start_date: "start_date_input",
      end_date: "end_date_input",
      side_effects_notes: "side_effects_notes_input",
      hospital_name: "hospital_name_input",
    },
    required: ["medication_name", "frequency"],
    title: "복용약물",
  },
};

// 공용 모달 열기: 각 health-item 클릭 시 모달 열기
document.addEventListener('DOMContentLoaded', function() {
  document.querySelectorAll(".health-item-compact.mdc").forEach((item) => {
    item.addEventListener("click", () => {
      const current_pet_id = localStorage.getItem('currentPetId')
      const name = item.dataset.modal; // 모달 종류
      if (!current_pet_id) {
        alert("펫을 먼저 선택해주세요.");
        return;
      }
      openModal(name, current_pet_id); // 모달 열기
    });
  });
});

// 모달 열기 함수
function openModal(name, pet_id) {
  console.log(`##### name ${name}, pet_id ${pet_id}`);
  
  // care_chatbot 모달인 경우 플로팅 버튼 숨기기
  if (name === 'care_chatbot') {
    const floatingBtn = document.querySelector('.floating-chat-btn');
    if (floatingBtn) {
      floatingBtn.style.display = 'none';
    }
  }
  
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
      closeBtn.onclick = () => {
        modal.classList.add("hidden");
        if (name === 'care_chatbot' && typeof showFloatingButton === 'function') {
          showFloatingButton();
        }
      };

      // 모달 바깥 클릭 시 닫기
      modal.onclick = (e) => {
        if (e.target === modal) {
          modal.classList.add("hidden");
          if (name === 'care_chatbot' && typeof showFloatingButton === 'function') {
            showFloatingButton();
          }
        }
      };

      // ---- 여기서 모달 내부 요소 접근 ----
      const hiddenInput = document.getElementById("modal-pet-id");
      const currentPetId = hiddenInput ? Number(hiddenInput.value) : pet_id;

      setupMedicalModal(name, pet_id);
    })

    .catch((err) => {
      console.error("모달 불러오기 실패:", err);
      alert("모달을 불러오지 못했습니다.");
      if (name === 'care_chatbot' && typeof showFloatingButton === 'function') {
        showFloatingButton();
      }
    });
}

// 모달 닫기 함수
function closeModal() {
  document.getElementById("common-modal").classList.add("hidden");
  // care_chatbot 모달이었다면 플로팅 버튼 다시 보이기
  if (typeof showFloatingButton === 'function') {
    showFloatingButton();
  }
  // location.reload();
}

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

// 의료기록 모달 공통 설정
function setupMedicalModal(modalType, pet_id) {
  // 모달 안에서만 찾기
  const modal = document.getElementById("common-modal");
  const saveBtn = modal.querySelector(".btn-primary");

  if (saveBtn) {
    saveBtn.onclick = (e) => {
      e.preventDefault();
      saveMedicalRecord(modalType, pet_id);
    };
  }
}

// 공통 의료기록 저장 함수
async function saveMedicalRecord(modalType, pet_id) {
  console.log(`save${modalType} pet_id:`, pet_id);

  const config = medicalConfigs[modalType];
  if (!config) {
    alert("지원하지 않는 모달 타입입니다.");
    return;
  }

  // 폼 데이터 수집
  const send_data = { pet_id: pet_id };

  for (const [key, inputId] of Object.entries(config.fields)) {
    const element = document.getElementById(inputId);
    if (element) {
      send_data[key] = element.value || null;
    }
  }

  // 필수 값 검증
  const missingFields = config.required.filter((field) => !send_data[field]);
  if (missingFields.length > 0) {
    alert(`다음 필수 항목을 입력해주세요: ${missingFields.join(", ")}`);
    return;
  }

  try {
    const response = await fetch(`/api/dailycares${config.endpoint}${pet_id}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(send_data),
    });

    if (!response.ok) {
      alert(`${config.title} 저장에 실패했습니다.`);
    } else {
      console.log(`${config.title} 저장 완료`);
      alert(`${config.title}이(가) 성공적으로 저장되었습니다.`);

      // 폼 초기화
      // resetForm(config.fields);

      // 모달 닫기
      closeModal();
    }
  } catch (error) {
    console.error("저장 오류:", error);
    alert("저장 중 오류가 발생했습니다.");
  }
}

// 폼 초기화
// function resetForm(fields) {
//   Object.values(fields).forEach((inputId) => {
//     const element = document.getElementById(inputId);
//     if (element) {
//       if (element.type === "select-one") {
//         element.selectedIndex = 0;
//       } else {
//         element.value = "";
//       }
//     }
//   });
// }
