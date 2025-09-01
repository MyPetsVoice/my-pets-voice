let currentCategory = "allergy";
let currentRecords = [];

// 카테고리 설정
const categories = {
  allergy: {
    name: "알러지",
    icon: "🤧",
    endpoint: "/allergy/",
    idField: "allergy_id",
  },
  disease: {
    name: "질병이력",
    icon: "🏥",
    endpoint: "/diseases/",
    idField: "disease_id",
  },
  surgery: {
    name: "수술이력",
    icon: "⚕️",
    endpoint: "/surgeries/",
    idField: "surgery_id",
  },
  vaccination: {
    name: "예방접종",
    icon: "💉",
    endpoint: "/vaccinations/",
    idField: "vaccination_id",
  },
  medication: {
    name: "복용약물",
    icon: "💊",
    endpoint: "/medications/",
    idField: "medication_id",
  },
};

// 페이지 로드 시 초기화
document.addEventListener("DOMContentLoaded", function () {
  initializePage();
  setupEventListeners();
  loadPetInfo();
  loadRecords("allergy");
});

// 페이지 초기화
function initializePage() {
  updateCategoryUI("allergy");
}

// 이벤트 리스너 설정
function setupEventListeners() {
  document.querySelectorAll(".category-tab").forEach((tab) => {
    tab.addEventListener("click", function () {
      const category = this.dataset.category;
      switchCategory(category);
    });
  });

  document
    .getElementById("detail-modal")
    .addEventListener("click", function (e) {
      if (e.target === this) {
        closeModal();
      }
    });

  document.addEventListener("keydown", function (e) {
    if (e.key === "Escape") {
      closeModal();
    }
  });
}

// 펫 정보 로드
async function loadPetInfo() {
  try {
    const response = await fetch(`/api/dailycares/pet-info/${CURRENT_PET_ID}`);
    const data = await response.json();
    if (data) {
      document.getElementById("pet-name").textContent = data.pet_name;
    }
  } catch (error) {
    console.error("펫 정보 로드 실패:", error);
    document.getElementById("pet-name").textContent = "반려동물";
  }
}

// 카테고리 전환
function switchCategory(category) {
  if (currentCategory === category) return;
  currentCategory = category;
  updateCategoryUI(category);
  loadRecords(category);
}

// 카테고리 UI 업데이트
function updateCategoryUI(category) {
  document.querySelectorAll(".category-tab").forEach((tab) => {
    tab.classList.remove("active");
  });
  document
    .querySelector(`[data-category="${category}"]`)
    .classList.add("active");

  document.getElementById("current-category").textContent =
    categories[category].name;
  document.getElementById("empty-category").textContent =
    categories[category].name;
}

// 기록 로드
async function loadRecords(category) {
  showLoading();

  try {
    const endpoint = `/api/dailycares${categories[category].endpoint}${CURRENT_PET_ID}`;
    const response = await fetch(endpoint);
    const records = await response.json();

    currentRecords = records || [];
    displayRecords(category, currentRecords);
  } catch (error) {
    console.error(`${category} 기록 로드 실패:`, error);
    showError("기록을 불러오는 중 오류가 발생했습니다.");
  }
}

// 로딩 상태 표시
function showLoading() {
  document.getElementById("loading-state").style.display = "block";
  document.getElementById("records-list").innerHTML = "";
  document.getElementById("empty-state").classList.add("hidden");
}

// 기록 표시
function displayRecords(category, records) {
  document.getElementById("loading-state").style.display = "none";
  document.getElementById("record-count").textContent = records.length;

  if (records.length === 0) {
    showEmptyState();
    return;
  }

  const recordsHtml = records
    .map((record) => {
      return createRecordCard(category, record);
    })
    .join("");

  document.getElementById("records-list").innerHTML = recordsHtml;
  document.getElementById("empty-state").classList.add("hidden");

  // 이벤트 리스너 추가
  setupRecordEvents(category, records);
}

// 기록 카드 이벤트 설정
function setupRecordEvents(category, records) {
  // 카드 클릭 이벤트 (상세보기)
  document.querySelectorAll(".record-card-content").forEach((content) => {
    content.addEventListener("click", function () {
      const recordId = this.closest(".record-card").dataset.recordId;
      const record = records.find(
        (r) => r[categories[category].idField] == recordId
      );
      showEditModal(category, record);
    });
  });

  // 삭제 버튼 이벤트
  document.querySelectorAll(".delete-btn").forEach((btn) => {
    btn.addEventListener("click", function (e) {
      e.stopPropagation(); // 카드 클릭 이벤트 방지
      const recordId = this.dataset.recordId;
      deleteRecord(category, recordId);
    });
  });
}

// 빈 상태 표시
function showEmptyState() {
  document.getElementById("records-list").innerHTML = "";
  document.getElementById("empty-state").classList.remove("hidden");
}

// 에러 표시
function showError(message) {
  document.getElementById("loading-state").style.display = "none";
  document.getElementById("records-list").innerHTML = `
    <div class="text-center py-12 text-red-500">
      <div class="text-4xl mb-4">⚠️</div>
      <p>${message}</p>
    </div>
  `;
}

// 수정/삭제 버튼이 있는 기록 카드 생성
function createRecordCard(category, record) {
  const recordId = record[categories[category].idField];

  let cardContent = "";

  switch (category) {
    case "allergy":
      cardContent = `
        <div class="record-title">${record.allergen}</div>
        <div class="record-meta">
          <span class="meta-item">
            <span class="meta-label">유형:</span> ${record.allergy_type}
          </span>
          <span class="severity-badge severity-${record.severity}">${
        record.severity
      }</span>
        </div>
        ${
          record.symptoms
            ? `<div class="record-summary">${truncateText(
                record.symptoms,
                100
              )}</div>`
            : ""
        }
      `;
      break;

    case "disease":
      cardContent = `
        <div class="record-title">${record.disease_name}</div>
        <div class="record-meta">
          ${
            record.diagnosis_date
              ? `<span class="meta-item"><span class="meta-label">진단일:</span> ${record.diagnosis_date}</span>`
              : ""
          }
          ${
            record.hospital_name
              ? `<span class="meta-item"><span class="meta-label">병원:</span> ${record.hospital_name}</span>`
              : ""
          }
          ${
            record.medical_cost
              ? `<span class="meta-item"><span class="meta-label">진료비:</span> ${Number(
                  record.medical_cost
                ).toLocaleString()}원</span>`
              : ""
          }
        </div>
        ${
          record.symptoms
            ? `<div class="record-summary">${truncateText(
                record.symptoms,
                100
              )}</div>`
            : ""
        }
      `;
      break;

    case "surgery":
      cardContent = `
        <div class="record-title">${record.surgery_name}</div>
        <div class="record-meta">
          ${
            record.surgery_date
              ? `<span class="meta-item"><span class="meta-label">수술일:</span> ${record.surgery_date}</span>`
              : ""
          }
          <span class="status-badge status-${record.recovery_status}">${
        record.recovery_status
      }</span>
          ${
            record.hospital_name
              ? `<span class="meta-item"><span class="meta-label">병원:</span> ${record.hospital_name}</span>`
              : ""
          }
        </div>
        ${
          record.surgery_summary
            ? `<div class="record-summary">${truncateText(
                record.surgery_summary,
                100
              )}</div>`
            : ""
        }
      `;
      break;

    case "vaccination":
      cardContent = `
        <div class="record-title">${record.vaccine_name}</div>
        <div class="record-meta">
          ${
            record.vaccination_date
              ? `<span class="meta-item"><span class="meta-label">접종일:</span> ${record.vaccination_date}</span>`
              : ""
          }
          ${
            record.hospital_name
              ? `<span class="meta-item"><span class="meta-label">병원:</span> ${record.hospital_name}</span>`
              : ""
          }
          ${
            record.manufacturer
              ? `<span class="meta-item"><span class="meta-label">제조사:</span> ${record.manufacturer}</span>`
              : ""
          }
        </div>
        ${
          record.next_vaccination_date
            ? `<div class="record-summary">다음 접종일: ${record.next_vaccination_date}</div>`
            : ""
        }
        ${
          record.side_effects
            ? `<div class="record-summary">${truncateText(
                record.side_effects,
                80
              )}</div>`
            : ""
        }
      `;
      break;

    case "medication":
      cardContent = `
        <div class="record-title">${record.medication_name}</div>
        <div class="record-meta">
          <span class="meta-item"><span class="meta-label">복용횟수:</span> ${
            record.frequency
          }</span>
          ${
            record.dosage
              ? `<span class="meta-item"><span class="meta-label">용량:</span> ${record.dosage}</span>`
              : ""
          }
          ${
            record.start_date
              ? `<span class="meta-item"><span class="meta-label">시작일:</span> ${record.start_date}</span>`
              : ""
          }
          ${
            record.end_date
              ? `<span class="meta-item"><span class="meta-label">종료일:</span> ${record.end_date}</span>`
              : ""
          }
        </div>
        ${
          record.purpose
            ? `<div class="record-summary">목적: ${truncateText(
                record.purpose,
                80
              )}</div>`
            : ""
        }
      `;
      break;

    default:
      return "";
  }

  return `
    <div class="record-card" data-record-id="${recordId}">
      <div class="record-card-content" style="cursor: pointer;">
        ${cardContent}
      </div>
      <div class="record-card-actions">
        <button class="delete-btn" data-record-id="${recordId}" title="삭제">
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"></path>
          </svg>
        </button>
      </div>
    </div>
  `;
}

// 수정 모달 표시
async function showEditModal(category, record) {
  try {
    const response = await fetch(
      `/api/dailycares/modal/${category}?pet_id=${CURRENT_PET_ID}`
    );
    const modalHtml = await response.text();

    document.getElementById("modal-content").innerHTML = modalHtml;
    bindModalData(category, record);

    // 모달 제목 변경
    const modalTitle = document.querySelector("#modal-content h2");
    if (modalTitle) {
      modalTitle.textContent = `${categories[category].name} 수정`;
    }

    // 저장 버튼을 수정 버튼으로 변경
    const saveBtn = document.querySelector(
      "#modal-content button[type='submit']"
    );
    if (saveBtn) {
      saveBtn.innerHTML = `
        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"></path>
        </svg>
        <span>수정</span>
      `;

      saveBtn.onclick = (e) => {
        e.preventDefault();
        updateRecord(category, record);
      };
    }

    document.getElementById("detail-modal").classList.remove("hidden");

    // 닫기 버튼 이벤트
    const closeBtn = document.querySelector(".close-modal-btn");
    if (closeBtn) {
      closeBtn.addEventListener("click", closeModal);
    }
  } catch (error) {
    console.error("모달 로드 실패:", error);
    showBasicModal(category, record);
  }
}

// 모달 데이터 바인딩
function bindModalData(category, record) {
  if (!record) return;

  switch (category) {
    case "allergy":
      setInputValue("allergy_type_select", record.allergy_type);
      setInputValue("allergen_input", record.allergen);
      setInputValue("symptoms_input", record.symptoms);
      setInputValue("severity_select", record.severity);
      break;

    case "disease":
      setInputValue("disease_name_input", record.disease_name);
      setInputValue("diagnosis_date_input", record.diagnosis_date);
      setInputValue("symptoms_input", record.symptoms);
      setInputValue("treatment_details_input", record.treatment_details);
      setInputValue("hospital_name_input", record.hospital_name);
      setInputValue("doctor_name_input", record.doctor_name);
      setInputValue("medical_cost_input", record.medical_cost);
      break;

    case "surgery":
      setInputValue("surgery_name_input", record.surgery_name);
      setInputValue("surgery_date_input", record.surgery_date);
      setInputValue("surgery_summary_input", record.surgery_summary);
      setInputValue("hospital_name_input", record.hospital_name);
      setInputValue("doctor_name_input", record.doctor_name);
      setInputValue("recovery_status_select", record.recovery_status);
      break;

    case "vaccination":
      setInputValue("vaccine_name_input", record.vaccine_name);
      setInputValue("vaccination_date_input", record.vaccination_date);
      setInputValue(
        "next_vaccination_date_input",
        record.next_vaccination_date
      );
      setInputValue("manufacturer_input", record.manufacturer);
      setInputValue("lot_number_input", record.lot_number);
      setInputValue("hospital_name_input", record.hospital_name);
      setInputValue("side_effects_input", record.side_effects);
      break;

    case "medication":
      setInputValue("medication_name_input", record.medication_name);
      setInputValue("purpose_input", record.purpose);
      setInputValue("dosage_input", record.dosage);
      setInputValue("frequency_select", record.frequency);
      setInputValue("start_date_input", record.start_date);
      setInputValue("end_date_input", record.end_date);
      setInputValue("side_effects_notes_input", record.side_effects_notes);
      setInputValue("hospital_name_input", record.hospital_name);
      break;
  }
}

// 입력 필드 값 설정
function setInputValue(elementId, value) {
  const element = document.getElementById(elementId);
  if (element && value !== null && value !== undefined) {
    element.value = value;
  }
}

// 기록 수정
async function updateRecord(category, record) {
  if (!confirm("정말 수정하시겠습니까?")) return;

  const recordId = record[categories[category].idField];
  const updateData = getFormData(category);

  try {
    const endpoint = `/api/dailycares/${category}/${recordId}`;
    const response = await fetch(endpoint, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(updateData),
    });

    if (response.ok) {
      alert("수정이 완료되었습니다.");
      closeModal();
      loadRecords(currentCategory); // 목록 새로고침
    } else {
      alert("수정에 실패했습니다.");
    }
  } catch (error) {
    console.error("수정 실패:", error);
    alert("수정 중 오류가 발생했습니다.");
  }
}

// 기록 삭제
async function deleteRecord(category, recordId) {
  if (!confirm("정말 삭제하시겠습니까?")) return;

  try {
    const endpoint = `/api/dailycares/${category}/${recordId}`;
    const response = await fetch(endpoint, { method: "DELETE" });

    if (response.ok) {
      alert("삭제가 완료되었습니다.");
      loadRecords(currentCategory); // 목록 새로고침
    } else {
      alert("삭제에 실패했습니다.");
    }
  } catch (error) {
    console.error("삭제 실패:", error);
    alert("삭제 중 오류가 발생했습니다.");
  }
}

// 폼 데이터 수집
function getFormData(category) {
  const data = {};

  switch (category) {
    case "allergy":
      data.allergy_type = document.getElementById("allergy_type_select")?.value;
      data.allergen = document.getElementById("allergen_input")?.value;
      data.symptoms = document.getElementById("symptoms_input")?.value;
      data.severity = document.getElementById("severity_select")?.value;
      break;

    case "disease":
      data.disease_name = document.getElementById("disease_name_input")?.value;
      data.diagnosis_date = document.getElementById(
        "diagnosis_date_input"
      )?.value;
      data.symptoms = document.getElementById("symptoms_input")?.value;
      data.treatment_details = document.getElementById(
        "treatment_details_input"
      )?.value;
      data.hospital_name = document.getElementById(
        "hospital_name_input"
      )?.value;
      data.doctor_name = document.getElementById("doctor_name_input")?.value;
      data.medical_cost = document.getElementById("medical_cost_input")?.value;
      break;

    case "surgery":
      data.surgery_name = document.getElementById("surgery_name_input")?.value;
      data.surgery_date = document.getElementById("surgery_date_input")?.value;
      data.surgery_summary = document.getElementById(
        "surgery_summary_input"
      )?.value;
      data.hospital_name = document.getElementById(
        "hospital_name_input"
      )?.value;
      data.doctor_name = document.getElementById("doctor_name_input")?.value;
      data.recovery_status = document.getElementById(
        "recovery_status_select"
      )?.value;
      break;

    case "vaccination":
      data.vaccine_name = document.getElementById("vaccine_name_input")?.value;
      data.vaccination_date = document.getElementById(
        "vaccination_date_input"
      )?.value;
      data.next_vaccination_date = document.getElementById(
        "next_vaccination_date_input"
      )?.value;
      data.manufacturer = document.getElementById("manufacturer_input")?.value;
      data.lot_number = document.getElementById("lot_number_input")?.value;
      data.hospital_name = document.getElementById(
        "hospital_name_input"
      )?.value;
      data.side_effects = document.getElementById("side_effects_input")?.value;
      break;

    case "medication":
      data.medication_name = document.getElementById(
        "medication_name_input"
      )?.value;
      data.purpose = document.getElementById("purpose_input")?.value;
      data.dosage = document.getElementById("dosage_input")?.value;
      data.frequency = document.getElementById("frequency_select")?.value;
      data.start_date = document.getElementById("start_date_input")?.value;
      data.end_date = document.getElementById("end_date_input")?.value;
      data.side_effects_notes = document.getElementById(
        "side_effects_notes_input"
      )?.value;
      data.hospital_name = document.getElementById(
        "hospital_name_input"
      )?.value;
      break;
  }

  return data;
}

// 모달 닫기
function closeModal() {
  document.getElementById("detail-modal").classList.add("hidden");
}

// 유틸리티 함수
function truncateText(text, maxLength) {
  if (!text) return "";
  return text.length > maxLength ? text.substring(0, maxLength) + "..." : text;
}

// 전역 함수
window.closeModal = closeModal;
