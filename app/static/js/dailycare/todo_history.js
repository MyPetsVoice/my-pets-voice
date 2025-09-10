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
  todoListDiv.innerHTML = "";

  if (!todos || todos.length === 0) {
    todoListDiv.innerHTML = `
      <div class="text-center py-10 text-gray-500">
        <i class="fas fa-inbox text-4xl mb-3"></i>
        <p class="text-lg font-medium">등록된 할 일이 없습니다.</p>
      </div>
    `;
    return;
  }

  todos.forEach((todo) => {
    const card = document.createElement("div");
    card.className =
      "bg-white rounded-xl shadow p-5 hover:shadow-md transition cursor-pointer";

    const todoDate = new Date(todo.todo_date).toLocaleDateString();

    card.innerHTML = `
      <div class="flex justify-between items-center mb-2">
        <h3 class="font-semibold text-lg text-gray-800">${todo.title}</h3>
        <span class="text-sm text-gray-500">${todoDate}</span>
      </div>
      <p class="text-gray-600 text-sm mb-3">${
        todo.description || "상세내용 없음"
      }</p>
      <div class="flex justify-between text-sm">
        <span class="px-2 py-1 rounded-full ${
          todo.status === "완료"
            ? "bg-green-100 text-green-700"
            : "bg-yellow-100 text-yellow-700"
        }">
          <i class="fas fa-${
            todo.status === "완료" ? "check-circle" : "clock"
          } mr-1"></i>${todo.status}
        </span>
        <span class="px-2 py-1 rounded-full ${
          todo.priority === "높음"
            ? "bg-red-100 text-red-700"
            : todo.priority === "보통"
            ? "bg-yellow-100 text-yellow-700"
            : "bg-green-100 text-green-700"
        }">
          <i class="fas fa-flag mr-1"></i>${todo.priority}
        </span>
      </div>
    `;

    card.addEventListener("click", () => {
      window.location.href = `/dailycare/todo?todo_id=${todo.todo_id}`;
    });

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
