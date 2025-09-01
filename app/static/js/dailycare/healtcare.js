document.addEventListener('DOMContentLoaded', ()=>{
    const pet_id = localStorage.getItem("currentPetId");
    console.log('petId : ',pet_id)
    if(!pet_id){
        alert('펫 정보가 존재하지 않습니다')
        return
    }

    getAllHealthcareLog(pet_id)
    getPetInfo(pet_id)
})

async function getPetInfo(pet_id){
  // 개별 펫 조회
  const response = await fetch(
    `/api/dailycares/pet-info/${pet_id}`
  );
  if (!response.ok) {
    pet_detail.innerHTML = "<p>Pet 정보를 불러올 수 없습니다.</p>";
    return;
  }
  const data = await response.json();
  const pets = Array.isArray(data) ? data : [data];
  console.log(data)
        const pet_info_div = document.getElementById("pet_info");
    pets.forEach((i) => {
      const result = document.createElement("div");
      
      result.innerHTML = ` 
         <!-- Pet Tags -->
                <div class="flex flex-wrap justify-center gap-3 mb-8">
                    <span class="pet-tag px-4 py-2 rounded-full text-white text-sm">${
                      i.pet_name
                    }</span>
                </div>
                
                <!-- Current Pet Info -->
                <div class="bg-white bg-opacity-20 backdrop-blur-sm rounded-2xl p-6 max-w-md mx-auto">
                    <h3 class="text-white font-semibold mb-2">${i.pet_name} (${
        i.pet_species
      })</h3>
                    <div class="text-white text-sm space-y-1">
                        <p>종: ${i.pet_breed}</p>
                        <p>나이: ${i.pet_age}</p>
                        <p>성별:  ${i.pet_gender}</p>
                        <p>중성화 여부: ${i.is_neutered ? "Yes" : "No"}</p>
                    </div>
                </div>`;
      pet_info_div.appendChild(result);
    });
  
}

async function getAllHealthcareLog(pet_id) {
    const response  = await fetch(`/api/dailycares/healthcare/${pet_id}`)
    const data = await response.json()
    console.log(data)
    if(data.length > 0 ){
        data.forEach(i => {
            const history = document.getElementById('history')
            const result = document.createElement('div')
            result.style.marginBottom = "15px";
            result.innerHTML = `
              <div class="card-hover bg-gradient-to-br from-yellow-50 to-orange-50 rounded-xl p-6 border border-yellow-200">
                                <div class="flex items-center mb-4">
                                    <div class="bg-yellow-100 p-3 rounded-full">
                                        <span class="text-2xl">📊</span>
                                    </div>
                                    <div class="ml-3">
                                        <h3 class="font-semibold text-gray-800">건강기록</h3>
                                        <p class="text-sm text-gray-600">음식, 환경 일일지 등록</p>
                                    </div>
                                </div>
                                
                                <!-- Record Details -->
                                <div class="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4" id="">
                                    <div class="text-center">
                                        <div class="text-2xl font-bold text-gray-800">${i.weight_kg}kg</div>
                                        <div class="text-sm text-gray-600">체중</div>
                                    </div>
                                    <div class="text-center">
                                        <div class="text-2xl font-bold text-gray-800">${i.water}ml</div>
                                        <div class="text-sm text-gray-600">수분 섭취</div>
                                    </div>
                                    <div class="text-center">
                                        <div class="text-2xl font-bold text-gray-800">${i.food}g</div>
                                        <div class="text-sm text-gray-600">사료량</div>
                                    </div>
                                    <div class="text-center">
                                        <div class="text-2xl font-bold text-gray-800">${i.walk_time_minutes}분</div>
                                        <div class="text-sm text-gray-600">산책 시간</div>
                                    </div>
                                </div>
                                
                                <div class="pt-4 border-t border-yellow-200">
                                    <div class="flex justify-between items-center mb-2">
                                        <span class="text-sm text-gray-500">배변 상태</span>
                                        <span class="bg-green-100 text-green-800 px-3 py-1 rounded-full text-sm font-medium">
                                            <i class="fas fa-check-circle mr-1"></i>${i.excrement_status}
                                        </span>
                                    </div>
                                    <div class="flex justify-between items-center">
                                        <span class="text-sm text-gray-500">기록 일시</span>
                                        <span class="text-sm text-gray-600">${i.updated_at}</span>
                                    </div>
                                </div>
                            </div>
                           
            `; 
            history.appendChild(result)
            
            
        });
    }
}

