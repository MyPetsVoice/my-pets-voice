import { pet_id } from "./dailycare.js";
console.log(pet_id);

window.addEventListener("petChanged", (e) => {
  const pet_id = e.detail;
  renderCalendar(current, pet_id);
});

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
  monthLabel.textContent = date.format("YYYY년 M월");
  grid.querySelectorAll(".calendar-day").forEach((e) => e.remove());

  const firstDay = date.startOf("month").day();
  const lastDate = date.endOf("month").date();

  // 시작 요일만큼 빈 칸 추가
  for (let i = 0; i < firstDay; i++) {
    grid.appendChild(document.createElement("div"));
  }

  // 📌 헬스케어 데이터 불러오기 (await 추가)
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

    // 📌 updated_at 기준으로 데이터 표시
    const hasData = healthcareData.some((care) => {
      const updated = dayjs(care.updated_at);
      return (
        updated.year() === date.year() &&
        updated.month() === date.month() &&
        updated.date() === d
      );
    });

    if (hasData) {
      cell.classList.add("has-data"); // 스타일링용 class
      const dot = document.createElement("span");
      dot.style.display = "block";
      dot.style.width = "6px";
      dot.style.height = "6px";
      dot.style.borderRadius = "50%";
      dot.style.backgroundColor = "blue";
      dot.style.margin = "0 auto";

      const careId = healthcareData.find(care => {
        const updated = dayjs(care.updated_at);
        return (
          updated.year() === date.year() &&
          updated.month() === date.month() &&
          updated.date() === d
        );
      })?.care_id;

      if (careId) {
        dot.dataset.careId = careId;
        cell.addEventListener("click", () => {
          window.location.href = `/dailycare/health-history?care_id=${careId}`;
        });
      }
    
      cell.appendChild(dot);
    }

    grid.appendChild(cell);
  }
}

// 이전/다음 달 이동 (async 추가)
document.getElementById("prev-month").onclick = async () => {
  current = current.subtract(1, "month");
  await renderCalendar(current, pet_id);
};

document.getElementById("next-month").onclick = async () => {
  current = current.add(1, "month");
  await renderCalendar(current, pet_id);
};

// 초기 렌더링 (async 처리)
(async () => {
  await renderCalendar(current, pet_id);
})();
