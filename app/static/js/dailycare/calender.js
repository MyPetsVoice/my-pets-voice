let today = dayjs();
let current = dayjs();
let isRendering = false; // 렌더링 중복 방지 플래그

const monthLabel = document.getElementById("current-month");
const grid = document.getElementById("calendar-grid");

function renderWeekdays() {
  const weekdays = ["일", "월", "화", "수", "목", "금", "토"];
  weekdays.forEach((day) => {
    const cell = document.createElement("div");
    cell.textContent = day;
    cell.classList.add("calendar-weekday");
    grid.appendChild(cell); // 👉 바로 grid에 추가
  });
}


// 📌 헬스케어 데이터 가져오기
async function renderHealthcare(pet_id) {
  try {
    const response = await fetch(`/api/dailycares/healthcare/pet/${pet_id}`);
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    const data = await response.json();
    console.log("render healthcare data : ", data);
    return data;
  } catch (error) {
    console.error("헬스케어 데이터를 가져오는 중 오류 발생:", error);
    return [];
  }
}

async function renderCalendar(date, pet_id) {
  // 이미 렌더링 중이면 중복 실행 방지
  if (isRendering) {
    console.log("이미 렌더링 중입니다. 중복 실행 방지됨");
    return;
  }

  isRendering = true;
  console.log("renderCalendar 실행", date.format("YYYY-MM"), pet_id);

  try {
    // ✅ 엘리먼트 존재 확인
    if (!grid || !monthLabel) {
      console.error("캘린더 요소를 찾을 수 없습니다");
      return;
    }

    // ✅ 초기화
    grid.innerHTML = "";
    monthLabel.textContent = date.format("YYYY년 M월");

  // 요일 헤더 먼저 출력
  renderWeekdays();

  const firstDay = date.startOf("month").day();
  const lastDate = date.endOf("month").date();

  // 시작 요일만큼 빈 칸 추가
  for (let i = 0; i < firstDay; i++) {
    const empty = document.createElement("div");
    empty.classList.add("calendar-empty");
    grid.appendChild(empty);
  }

  // 📌 헬스케어 데이터 (펫이 없으면 빈 배열)
  const healthcareData = pet_id ? await renderHealthcare(pet_id) : [];

  for (let d = 1; d <= lastDate; d++) {
    const cell = document.createElement("div");
    cell.textContent = d;
    cell.classList.add("calendar-day");

    // 오늘 날짜 표시
    if (
      date.year() === today.year() &&
      date.month() === today.month() &&
      d === today.date()
    ) {
      cell.classList.add("today");
    }

    if (pet_id) {
      // 📌 updated_at 기준으로 데이터 표시
      const matchedCare = healthcareData.find((care) => {
        const updated = dayjs(care.updated_at);
        return (
          updated.year() === date.year() &&
          updated.month() === date.month() &&
          updated.date() === d
        );
      });

      if (matchedCare) {
        cell.classList.add("has-data");

        const dot = document.createElement("span");
        dot.style.display = "block";
        dot.style.width = "6px";
        dot.style.height = "6px";
        dot.style.borderRadius = "50%";
        dot.style.backgroundColor = "blue";
        dot.style.margin = "0 auto";

        if (matchedCare.care_id) {
          dot.dataset.careId = matchedCare.care_id;
          cell.addEventListener("click", () => {
            window.location.href = `/dailycare/health-history?care_id=${matchedCare.care_id}`;
          });
        }

        cell.appendChild(dot);
      }
    }

    grid.appendChild(cell);
  }
  } catch (error) {
    console.error("캘린더 렌더링 오류:", error);
  } finally {
    // 렌더링 완료 후 플래그 해제
    isRendering = false;
  }
}

// 🔹 이전/다음 달 이동 → 매번 최신 pet_id 읽기 (디바운싱 적용)
document.getElementById("prev-month").onclick = async () => {
  if (isRendering) return; // 렌더링 중이면 무시
  
  current = current.subtract(1, "month");
  const pet_id = localStorage.getItem("currentPetId");
  await renderCalendar(current, pet_id);
};

document.getElementById("next-month").onclick = async () => {
  if (isRendering) return; // 렌더링 중이면 무시
  
  current = current.add(1, "month");
  const pet_id = localStorage.getItem("currentPetId");
  await renderCalendar(current, pet_id);
};

// 🔹 펫 변경 이벤트 반영 (단일 진입점)
window.addEventListener("petChanged", async () => {
  if (isRendering) return; // 렌더링 중이면 무시
  
  const pet_id = localStorage.getItem("currentPetId");
  console.log("펫 변경됨 → 달력 갱신", pet_id);
  await renderCalendar(current, pet_id);
});

// ✅ 페이지 로드 시 바로 현재 달 렌더링
window.addEventListener("DOMContentLoaded", async () => {
  const pet_id = localStorage.getItem("currentPetId");
  console.log("페이지 로드됨, pet_id:", pet_id);
  await renderCalendar(current, pet_id);  // 초기 로드시 달력 출력
});

window.addEventListener('healthcareSaved', async (e) =>{
  if (isRendering) return; // 렌더링 중이면 무시
  
  console.log('건강기록이 저장됐습니다 캘린더를 갱신하겠습니다')
  await renderCalendar(current, e.detail.pet_id)
})
