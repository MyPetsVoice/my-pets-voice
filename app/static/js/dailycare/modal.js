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

      setupMedicalModal(name, pet_id);
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

// 의료기록 모달 공통 설정 (목록 로드 제거)
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
      resetForm(config.fields);

      // 모달 닫기
      closeModal();
    }
  } catch (error) {
    console.error("저장 오류:", error);
    alert("저장 중 오류가 발생했습니다.");
  }
}

// 폼 초기화
function resetForm(fields) {
  Object.values(fields).forEach((inputId) => {
    const element = document.getElementById(inputId);
    if (element) {
      if (element.type === "select-one") {
        element.selectedIndex = 0;
      } else {
        element.value = "";
      }
    }
  });
}

// 아직 사용하지 않는 함수들
// async function loadMedicalRecords(modalType, pet_id) {
//   const config = medicalConfigs[modalType];
//   if (!config) return;

//   try {
//     const response = await fetch(
//       `/api/dailycares${config.listEndpoint}${pet_id}`
//     );
//     const records = await response.json();

//     displayMedicalRecords(modalType, records);
//   } catch (error) {
//     console.error(`${config.title} 목록 로드 실패:`, error);
//   }
// }

// function displayMedicalRecords(modalType, records) {
//   const listContainer = document.getElementById(`${modalType}-list`);
//   if (!listContainer) return;

//   const config = medicalConfigs[modalType];

//   if (records.length === 0) {
//     listContainer.innerHTML = `<p style="text-align: center; color: #999;">등록된 ${config.title}가 없습니다.</p>`;
//     return;
//   }

//   const listHTML = records
//     .map((record) => {
//       return createRecordCard(modalType, record);
//     })
//     .join("");

//   listContainer.innerHTML = listHTML;
// }

// function createRecordCard(modalType, record) {
//   const getIdField = (type) => {
//     switch (type) {
//       case "allergy":
//         return record.allergy_id;
//       case "disease":
//         return record.disease_id;
//       case "surgery":
//         return record.surgery_id;
//       case "vaccination":
//         return record.vaccination_id;
//       case "medication":
//         return record.medication_id;
//     }
//   };

//   const getTitle = (type, record) => {
//     switch (type) {
//       case "allergy":
//         return record.allergen;
//       case "disease":
//         return record.disease_name;
//       case "surgery":
//         return record.surgery_name;
//       case "vaccination":
//         return record.vaccine_name;
//       case "medication":
//         return record.medication_name;
//     }
//   };

//   const getSubInfo = (type, record) => {
//     switch (type) {
//       case "allergy":
//         return `${record.allergy_type} | ${record.severity}`;
//       case "disease":
//         return record.diagnosis_date ? `진단일: ${record.diagnosis_date}` : "";
//       case "surgery":
//         return `${record.surgery_date} | ${record.recovery_status}`;
//       case "vaccination":
//         return record.vaccination_date
//           ? `접종일: ${record.vaccination_date}`
//           : "";
//       case "medication":
//         return `${record.frequency} | ${record.dosage || ""}`;
//     }
//   };

//   return `
//     <div style="background: #f9f9f9; padding: 15px; border-radius: 8px; margin-bottom: 10px;">
//       <div style="display: flex; justify-content: space-between; align-items: start;">
//         <div style="flex: 1;">
//           <h4 style="margin: 0 0 5px 0; font-weight: 600;">${getTitle(
//             modalType,
//             record
//           )}</h4>
//           <p style="margin: 0; font-size: 14px; color: #666;">${getSubInfo(
//             modalType,
//             record
//           )}</p>
//           ${
//             record.symptoms
//               ? `<p style="margin: 5px 0 0 0; font-size: 13px; color: #888;">${record.symptoms}</p>`
//               : ""
//           }
//         </div>
//         <button onclick="deleteMedicalRecord('${modalType}', ${getIdField(
//     modalType
//   )})"
//                 style="background: none; border: none; color: #e53e3e; cursor: pointer; padding: 5px;">
//           삭제
//         </button>
//       </div>
//     </div>
//   `;
// }

// async function deleteMedicalRecord(modalType, recordId) {
//   const config = medicalConfigs[modalType];
//   if (!confirm(`정말 이 ${config.title}을(를) 삭제하시겠습니까?`)) {
//     return;
//   }

//   const deleteEndpoint = `/${modalType}/${recordId}`;

//   try {
//     const response = await fetch(`/api/dailycares${deleteEndpoint}`, {
//       method: "DELETE",
//     });

//     if (response.ok) {
//       alert("삭제되었습니다.");
//       loadMedicalRecords(modalType, current_pet_id);
//     } else {
//       alert("삭제에 실패했습니다.");
//     }
//   } catch (error) {
//     console.error("삭제 오류:", error);
//     alert("삭제 중 오류가 발생했습니다.");
//   }
// }

// function getSeverityColor(severity) {
//   switch (severity) {
//     case "경미":
//       return "green";
//     case "보통":
//       return "yellow";
//     case "심각":
//       return "red";
//     default:
//       return "gray";
//   }
// }

// function getRecoveryColor(status) {
//   switch (status) {
//     case "완전회복":
//       return "green";
//     case "회복중":
//       return "blue";
//     case "경과관찰중":
//       return "yellow";
//     default:
//       return "gray";
//   }
// }
