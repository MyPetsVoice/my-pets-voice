// 달력 렌더링
let today = dayjs();
let current = dayjs();
const monthLabel = document.getElementById("current-month");
const grid = document.getElementById("calendar-grid");

function renderCalendar(date) {
  monthLabel.textContent = date.format("YYYY년 M월");
  grid.querySelectorAll(".calendar-day").forEach((e) => e.remove());

  const firstDay = date.startOf("month").day();
  const lastDate = date.endOf("month").date();

  for (let i = 0; i < firstDay; i++)
    grid.appendChild(document.createElement("div"));

  for (let d = 1; d <= lastDate; d++) {
    const cell = document.createElement("div");
    cell.textContent = d;
    cell.classList.add("calendar-day");
    if (
      date.year() === today.year() &&
      date.month() === today.month() &&
      d === today.date()
    )
      cell.classList.add("today");
    grid.appendChild(cell);
  }
}

document.getElementById("prev-month").onclick = () => {
  current = current.subtract(1, "month");
  renderCalendar(current);
};
document.getElementById("next-month").onclick = () => {
  current = current.add(1, "month");
  renderCalendar(current);
};
renderCalendar(current);
