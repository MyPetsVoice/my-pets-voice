document.addEventListener('DOMContentLoaded',()=>{
    const petElement = document.querySelector(".todo");
    const todoId = petElement.getAttribute("data-todo-id");
    console.log("todoId : ", todoId); 
    document.getElementById("delete_btn").addEventListener('click',()=>{
        deleteTodo(todoId)
    });
})

async function deleteTodo(todo_id){
    const confirmed = confirm('삭제하시겠습니까?')
    if(!confirmed) return
    const response = await fetch(`/api/dailycares/todo/${todo_id}`,{
        method : 'DELETE',
        headers : {'Content-Type' : 'application/json'}

    })

    if(!response.ok){
        throw new Error('삭제에 실패했습니다')
    }else{
        alert('성공적으로 삭제되었습니다')
        window.location.href = `/dailycare/todo`
    }

}