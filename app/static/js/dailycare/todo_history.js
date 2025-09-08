document.addEventListener("DOMContentLoaded", () => {
  allTodoLog();
  // 필터 버튼 이벤트
  document.querySelectorAll(".filter-btn").forEach((btn) => {
    btn.addEventListener("click", (e) => {
      const filter = e.currentTarget.dataset.filter;
      filterTodos(filter);
    });
  });
});

let allTodos = []; // 전체 Todo 데이터를 저장

async function allTodoLog() {
  try {
    const response = await fetch(`/api/dailycares/todo/all/`);
    if (!response.ok) throw new Error("Todo 데이터를 가져오지 못했습니다.");
    allTodos = await response.json();
    console.log(allTodos)
    renderTodos(allTodos);
    updateStatistics(allTodos);
  } catch (err) {
    console.error("Todo 조회 실패:", err);
  }
}

function renderTodos(todos) {
  const todoListDiv = document.getElementById("todoList");
  if (!todoListDiv) return;

  todoListDiv.innerHTML = ""; // 초기화

  todos.forEach((todo) => {
    const card = document.createElement("div");
    card.className = "bg-white rounded-xl p-6 shadow-md border border-gray-200";

    const createdAt = new Date(todo.created_at).toLocaleString();
    const updatedAt = new Date(todo.updated_at).toLocaleString();
    const todoDate = new Date(todo.todo_date).toLocaleDateString();

    card.innerHTML = `
      <div class="flex justify-between items-center mb-2">
        <h3 class="font-semibold text-gray-800 text-lg">${todo.title}</h3>
        <span class="text-sm text-gray-500">${todoDate}</span>
      </div>
      <p class="text-gray-600 mb-4">${todo.description || ""}</p>
      <div class="flex space-x-4 mb-4">
        <div class="text-sm">
          <span class="font-medium text-gray-700">우선순위:</span> ${
            todo.priority
          }
        </div>
        <div class="text-sm">
          <span class="font-medium text-gray-700">상태:</span> ${todo.status}
        </div>
      </div>
      <div class="flex justify-between text-sm text-gray-500 border-t pt-2">
        <span>생성: ${createdAt}</span>
        <span>수정: ${updatedAt}</span>
      </div>
    `;

    card.addEventListener('click', ()=>{
      window.location.href = `/dailycare/todo?todo_id=${todo.todo_id}`
    })

    todoListDiv.appendChild(card);

  });
}

// 필터 적용 함수
function filterTodos(filter) {
  document.querySelectorAll(".filter-btn").forEach((btn) => {
    if (btn.dataset.filter === filter) {
      // 선택된 버튼에 강조 클래스 추가
      btn.classList.add("bg-orange-500", "text-white", "border-orange-500");
      btn.classList.remove("bg-white", "text-gray-700", "border-gray-300");
    } else {
      // 나머지 버튼은 원래 상태
      btn.classList.remove("bg-orange-500", "text-white", "border-orange-500");
      btn.classList.add("bg-white", "text-gray-700", "border-gray-300");
    }
  });

  let filtered = allTodos;

  if (filter === "미완료" || filter === "완료") {
    filtered = allTodos.filter((todo) => todo.status === filter);
  } else if (filter === "높음") {
    filtered = allTodos.filter((todo) => todo.priority === filter);
  }

  renderTodos(filtered);
}


// 통계 업데이트 함수
function updateStatistics(todos) {
  const totalCount = todos.length;
  const pendingCount = todos.filter((t) => t.status === "미완료").length;
  const completedCount = todos.filter((t) => t.status === "완료").length;
  const highPriorityCount = todos.filter((t) => t.priority === "높음").length;

  document.getElementById("totalCount").textContent = totalCount;
  document.getElementById("pendingCount").textContent = pendingCount;
  document.getElementById("completedCount").textContent = completedCount;
  document.getElementById("highPriorityCount").textContent = highPriorityCount;
}
