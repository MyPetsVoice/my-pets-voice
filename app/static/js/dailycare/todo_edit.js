document.addEventListener('DOMContentLoaded',()=>{
    const todoElement = document.querySelector(".todo");
    const todoId = todoElement.getAttribute("data-todo-id");
    console.log("todoId : ", todoId); 
    document.getElementById('edit_btn').addEventListener('click',()=>{
        updateTodo(todoId)
    })
    document.getElementById('redirect_btn').addEventListener('click',(e)=>{
        e.preventDefault()
        window.location.href =  `/dailycare/todo`
    })


})

async function updateTodo(todo_id) {

  // 폼에서 값 읽기
  const title = document.getElementById("title").value;
  const description = document.getElementById("description").value;
  const status = document.getElementById("status").value;
  const priority = document.getElementById("priority").value;

  const send_data = {
    title,
    description,
    status,
    priority
  };

  try {
    const response = await fetch(`/api/dailycares/todo/${todo_id}`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(send_data)
    });

    if (!response.ok) throw new Error("Todo 업데이트 실패");

    alert("Todo가 성공적으로 수정되었습니다!");
    window.location.href = `/dailycare/todo?todo_id=${todo_id}`;
  } catch (err) {
    console.error(err);
    alert("수정 중 오류가 발생했습니다.");
  }
}
