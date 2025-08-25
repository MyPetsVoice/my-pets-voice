const user_id = 1;
const pet_selector = document.getElementById("pet-selector");
const pet_detail = document.getElementById("pet-detail");
let current_pet_id = null;
// 전체 펫 조회
async function getAllPetsById(user_id) {
  try {
    const response = await fetch(`/api/dailycares/get-pet/${user_id}`);
    if (!response.ok) throw new Error("Failed to fetch pet list");
    const pets = await response.json();
    console.log("회원의 petList입니다. ", pets);

    // pet-card 생성 (전체 pet)
    pets.forEach((pet, i) => {
      const card = document.createElement("div");
      card.className = "pet-card";
      // if (i === 0) {
      //   card.classList.add("active");
      //   current_pet_id = pet.pet_id; // 첫 번째 pet 기본 active 시 current_pet_id 설정
      // }
      card.dataset.petId = pet.pet_id;
      
      card.innerHTML = `<strong>${pet.pet_name}</strong><small>${pet.pet_breed}</small>`;
      pet_selector.appendChild(card);
    });

    // 클릭 (개별 pet 정보)
    pet_selector.querySelectorAll(".pet-card").forEach((card) => {
      card.addEventListener("click", async function () {
        // active 표시
        pet_selector
          .querySelectorAll(".pet-card")
          .forEach((c) => c.classList.remove("active"));
        this.classList.add("active");

  
        current_pet_id = this.dataset.petId;
        // 개별 펫 조회
        const response = await fetch(
          `/api/dailycares/get-pet/${user_id}/${current_pet_id}`
        );
        if (!response.ok) {
          pet_detail.innerHTML = "<p>Pet 정보를 불러올 수 없습니다.</p>";
          return;
        }
        const petData = await response.json();
        console.log("선택된 pet 데이터:", petData);
        getMedications(current_pet_id);
       

       
        pet_detail.innerHTML = `
          <h3>${petData.pet_name} (${petData.pet_species})</h3>
          <p>종: ${petData.pet_breed}</p>
          <p>나이: ${petData.pet_age}</p>
          <p>성별: ${petData.pet_gender}</p>
          <p>중성화 여부: ${petData.is_neutered ? "Yes" : "No"}</p>
        `;
      });

      
    });
  } catch (error) {
    console.error(error);
    pet_selector.innerHTML = "<p>Pet 리스트를 불러올 수 없습니다.</p>";
  }
}// end getAllPetsById

// 페이지 로딩 시 실행
getAllPetsById(user_id);
// 
const medicationSelect = document.getElementById("medication-select");
// pet에 medication정보 불러오기
async function getMedications(pet_id){
  const response = await fetch(`/api/dailycares/medications/${pet_id}`)
  if (!response.ok){
    throw new Error('영양제 목록을 불러오는데 실패했습니다.')
  }
  const data = await response.json()
  console.log(data)

  medicationSelect.innerHTML = ''
  if(data.length > 0){
  data.forEach((med)=>{
    const option = document.createElement('option')
    option.value = med.medication_id
    option.textContent = med.medication_name
    medicationSelect.appendChild(option)
  })}
  else{
    console.log('약/영양제 정보가 존재하지 않습니다.')
    const option = document.createElement('option')
    option.textContent = '약/영양제 정보가 없습니다. 약/영양제를 추가해주세요'
    option.style.disabled = true
    medicationSelect.appendChild(option);
  }
}// end getMedications(pet_id)


document
  .getElementById("save_healthcare")
  .addEventListener("click", async()=> {
    if(!confirm('오늘의 건강기록을 저장하시겠습니까?')){
      return
    }
    await saveHealthcare(current_pet_id)
  });

async function saveHealthcare(pet_id){
  const activePet = document.querySelector(".pet-card.active");
  if (!activePet) {
    alert("pet을 선택해주세요");
  }
  console.log(`현재 pet_id ${pet_id}`);
  console.log("save 중입니다.");
  const send_data = {
    pet_id: pet_id,
    food: document.getElementById("food-input").value,
    water: document.getElementById("water-input").value,
    excrement_status: document.getElementById("poop-select").value,
    weight_kg: document.getElementById("weight-input").value,
    walk_time_minutes: document.getElementById("walk-input").value,
    medication_ids: Array.from(medicationSelect.selectedOptions)
      .map((opt) => parseInt(opt.value))
      .filter((id) => !isNaN(id)),
  };

  console.log("저장할 정보입니다 : ", send_data);

  const response = await fetch(`/api/dailycares/save/healthcare/${pet_id}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(send_data),
  });

  if (!response.ok) {
    alert("기록저장이 실패되었습니다.");
  } else {
    console.log("기록저장완료");
  }
  // ✅ 입력값 초기화
  document.getElementById("food-input").value = "";
  document.getElementById("water-input").value = "";
  document.getElementById("poop-select").selectedIndex = 0; // select 첫 옵션으로
  document.getElementById("weight-input").value = "";
  document.getElementById("walk-input").value = "";
  medicationSelect.selectedIndex = -1; // multi select 초기화
  
} // end saveHealthCares





