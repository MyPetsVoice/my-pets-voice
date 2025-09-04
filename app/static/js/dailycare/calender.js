let today = dayjs();
let current = dayjs();

const monthLabel = document.getElementById("current-month");
const grid = document.getElementById("calendar-grid");

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
  console.log("renderCalendar 실행");

  if (!pet_id) {
    grid.innerHTML = "<p>펫을 선택해주세요 🐾</p>";
    monthLabel.textContent = date.format("YYYY년 M월");
    return;
  }

  // ✅ 초기화
  grid.innerHTML = "";
  monthLabel.textContent = date.format("YYYY년 M월");

  const firstDay = date.startOf("month").day();
  const lastDate = date.endOf("month").date();

  // 시작 요일만큼 빈 칸 추가
  for (let i = 0; i < firstDay; i++) {
    grid.appendChild(document.createElement("div"));
  }

  // 📌 헬스케어 데이터 불러오기
  const healthcareData = await renderHealthcare(pet_id);

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
      cell.classList.add("has-data"); // 스타일링용 class

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

    grid.appendChild(cell);
  }
}

// 🔹 이전/다음 달 이동 → 매번 최신 pet_id 읽기
document.getElementById("prev-month").onclick = async () => {
  current = current.subtract(1, "month");
  const pet_id = localStorage.getItem("currentPetId");
  await renderCalendar(current, pet_id);
};

document.getElementById("next-month").onclick = async () => {
  current = current.add(1, "month");
  const pet_id = localStorage.getItem("currentPetId");
  await renderCalendar(current, pet_id);
};

// 🔹 펫 변경 이벤트 반영 (단일 진입점)
window.addEventListener("petChanged", async () => {
  const pet_id = localStorage.getItem("currentPetId");
  if (!pet_id) return;
  console.log("펫 변경됨 → 달력 갱신", pet_id);
  await renderCalendar(current, pet_id);
});


