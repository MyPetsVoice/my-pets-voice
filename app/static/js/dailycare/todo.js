document.getElementById("create_todo").addEventListener("click", (e) => {
  const userIdElement = document.getElementById("user-id");
  const user_id = Number(userIdElement.value);
  console.log(user_id);
  console.log("userId", user_id);
  openModalTodo("todo", user_id);
 
    const dateInput = document.getElementById("todo_date_input");
    if (dateInput && !dateInput.value) {
      const today = new Date().toISOString().split("T")[0]; // YYYY-MM-DD
      dateInput.value = today;
    
    }
});

// 모달 열기 함수
function openModalTodo(name, user_id) {
  console.log(`##### name ${name}, user_id ${user_id}`);
  fetch(`/api/dailycares/modal/${name}?user_id=${user_id}`)
    .then((res) => {
      if (!res.ok) throw new Error("네트워크 오류");
      return res.text();
    })
    .then((html) => {
      const modal = document.getElementById("common-modal");
      const content = modal.querySelector("#modalContent");

      // 서버에서 받은 HTML 삽입
      content.innerHTML = html;
      // 오늘 날짜 기본값 세팅
      const dateInput = document.getElementById("todo_date_input");
      if (dateInput && !dateInput.value) {
        const today = new Date().toISOString().split("T")[0]; // YYYY-MM-DD
        dateInput.value = today;
      }
      modal.classList.remove("hidden");

      // 닫기 버튼 이벤트
      const closeBtn = document.getElementById("modal-close-btn");
      closeBtn.onclick = () => modal.classList.add("hidden");

      const saveBtn = document.getElementById("save_schedule_button");
      if (saveBtn) {
        saveBtn.onclick = (e) => {
          e.preventDefault();
          console.log("click");
          createTodo(user_id);
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




async function createTodo() {
  const send_data = {
    // user_id가 user_nickname이라서 삭제
    todo_date: document.getElementById("todo_date_input").value,
    title: document.getElementById("title_input").value,
    description: document.getElementById("description_input").value,
    status: document.getElementById("status_option").value,
    priority: document.getElementById("priority_option").value,
  };

  console.log("보낼 데이터 ", send_data);
  const response = await fetch(`/api/dailycares/save/todo/`, {
    method: "POST",
    headers: { "Content-type": "application/json" },
    body: JSON.stringify(send_data),
  });

  if (!response.ok) {
    alert("기록 저장에 실패했습니다.");
  } else {
    console.log("기록 저장 완료");
    closeModal();
  }
}
