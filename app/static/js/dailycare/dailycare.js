

const user_id = 1;
const pet_selector = document.getElementById("pet-selector");
const pet_detail = document.getElementById("pet-detail");

// 전체 펫 조회
async function getAllPetsById(user_id) {
  try {
    const response = await fetch(`/api/dailycares/get-pet/${user_id}`);
    if (!response.ok) throw new Error("Failed to fetch pet list");
    const pets = await response.json();
    console.log("회원의 petList입니다. ", pets);

    // pet-card 생성
    pets.forEach((pet, i) => {
      const card = document.createElement("div");
      card.className = "pet-card";
      if (i === 0) card.classList.add("active"); // 첫 번째 pet 기본 active
      card.dataset.petId = pet.pet_id;
      card.innerHTML = `<strong>${pet.pet_name}</strong><small>${pet.pet_breed}</small>`;
      pet_selector.appendChild(card);
    });

    // 클릭
    pet_selector.querySelectorAll(".pet-card").forEach((card) => {
      card.addEventListener("click", async function () {
        // active 표시
        pet_selector
          .querySelectorAll(".pet-card")
          .forEach((c) => c.classList.remove("active"));
        this.classList.add("active");

  
        const pet_id = this.dataset.petId;
        // 개별 펫 조회
        const response = await fetch(`/api/dailycares/get-pet/${user_id}/${pet_id}`);
        if (!response.ok) {
          pet_detail.innerHTML = "<p>Pet 정보를 불러올 수 없습니다.</p>";
          return;
        }
        const petData = await response.json();
        console.log("선택된 pet 데이터:", petData);
        getMedications(pet_id);

       
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
}

// 페이지 로딩 시 실행
getAllPetsById(user_id);
const medicationSelect = document.getElementById("medication-select");

async function getMedications(pet_id){
  const response = await fetch(`/api/dailycares/medications/${pet_id}`)
  if (!response.ok){
    throw new Error('영양제 목록을 불러오는데 실패했습니다.')
  }
  const data = await response.json()
  console.log(data)

  medicationSelect.innerHTML = ''
  data.forEach((med)=>{
    const option = document.createElement('option')
    option.value = med.medication_id
    option.textContent = med.medication_name
    medicationSelect.appendChild(option)
  })
}// end getMedications(pet_id)





