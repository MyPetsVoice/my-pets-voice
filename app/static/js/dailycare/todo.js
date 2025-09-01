document.getElementById("create_todo").addEventListener("click", (e) => {
  const userId = e.currentTarget.dataset.userId;
  console.log("userId", userId);
  openModalTodo("todo", userId);
});

// 모달 열기 함수
function openModalTodo(name, user_id) {
  console.log(`##### name ${name}, pet_id ${user_id}`);
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
      modal.classList.remove("hidden");

      // 닫기 버튼 이벤트
      const closeBtn = document.getElementById("modal-close-btn");
      closeBtn.onclick = () => modal.classList.add("hidden");

      // ---- 여기서 모달 내부 요소 접근 ----
      const hiddenInput = document.getElementById("modal-pet-id");
      const currentUserId = hiddenInput ? Number(hiddenInput.value) : user_id;

      // 저장 버튼 이벤트 등록 (중복 방지 위해 먼저 초기화)
      const saveBtn = document.getElementById("save_todo_button");
      if (saveBtn) {
        saveBtn.onclick = () => {
          console.log("click button");
          saveTodo(currentUserId);
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

function create_todo(user_id){
  const send_data = {
    user_id : user_id,
    todo_date : document.getElementById(),
    title : document.getElementById(),
    description : document.getElementById(),
    status : document.getElementById(),
    priority : document.getElementById(),
    
  }
  fetch(`/api/dailycares/save/todo/${user_id}`)
  .then()
}