
document.addEventListener('DOMContentLoaded', ()=>{
  const urlParams = new URLSearchParams(window.location.search);
  console.log(urlParams);
  const care_id = urlParams.get("care_id");
  console.log("care_id", care_id);
  const petElement = document.querySelector(".pet");
  const petId = petElement.getAttribute("data-pet-id");
  console.log('petId : ', petId); 
  document.getElementById("delete-btn").addEventListener("click", () => {
    deleteHealthcare(care_id);
  });
  const updateBtn = document.getElementById("edit-btn");
  updateBtn.addEventListener('click',()=>{
    window.location.href =  `/dailycare/update/health-care?care_id=${care_id}`
  })


})


async function deleteHealthcare(care_id) {
    const userConfirmed = confirm('삭제하시겠습니까?');
    if (!userConfirmed) return;

    try {
    const response = await fetch(`/api/dailycares/delete/healthcare/${care_id}`, {
        method: 'DELETE',
        headers: {
            'Content-Type': 'application/json'
        }
    });

        if (!response.ok) {
            throw new Error('삭제에 실패했습니다.');
        }else{

        alert('성공적으로 삭제되었습니다.');
        window.location.href = '/dailycare/health-history';}
    } catch (error) {
        console.error(error);
        alert('헬스케어 삭제중 오류가 발생했습니다.');
    }
}


