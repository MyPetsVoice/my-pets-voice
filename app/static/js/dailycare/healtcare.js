document.addEventListener('DOMContentLoaded', () => {
    const history = document.getElementById("history");
    if (!history) return;

    // 이벤트 위임
    history.addEventListener("click", (e) => {
        const card = e.target.closest(".card-hover");
        if (!card) return;
        const care_id = card.dataset.careId;
        window.location.href = `/dailycare/health-history?care_id=${care_id}`;
    });

    const pet_id = localStorage.getItem("currentPetId");
    console.log('petId : ', pet_id)
    if (!pet_id) {
        alert('펫 정보가 존재하지 않습니다');
        return;
    }
    getAllHealthcareLog(pet_id);
    getPetInfo(pet_id);
});


async function getPetInfo(pet_id){
  // 개별 펫 조회
  const response = await fetch(
    `/api/dailycares/pet-info/${pet_id}`
  );
  if (!response.ok) {
    console.error("Pet 정보를 불러올 수 없습니다.");
    return;
  }
  const data = await response.json();
  const pets = Array.isArray(data) ? data : [data];
  console.log(data);
  
  // 제목 부분에 동물 이름 표시
  const petNameDisplay = document.getElementById("pet-name-display");
  if (petNameDisplay && pets.length > 0) {
    petNameDisplay.textContent = `${pets[0].pet_name}의 건강기록 관리`;
  }
}

async function getAllHealthcareLog(pet_id) {
    const response  = await fetch(`/api/dailycares/healthcare/pet/${pet_id}`)
    const data = await response.json()
    console.log(data)
    if(data.length > 0 ){
        data.forEach(i => {
          const history = document.getElementById("history");
          const result = document.createElement("div");
          result.style.marginBottom = "15px";

          // 1️⃣ UTC 기준 날짜 생성
          const updatedAtUTC = new Date(i.updated_at);

          // 2️⃣ KST 변환: UTC + 9시간
          const updatedAtKST = new Date(
            updatedAtUTC.getTime() + 9 * 60 * 60 * 1000
          );

          // 3️⃣ 포맷팅
          const year = updatedAtKST.getFullYear();
          const month = String(updatedAtKST.getMonth() + 1).padStart(2, "0"); // 0~11 → 1~12
          const day = String(updatedAtKST.getDate()).padStart(2, "0");
          const hour = String(updatedAtKST.getHours()).padStart(2, "0");
          const minute = String(updatedAtKST.getMinutes()).padStart(2, "0");
          const second = String(updatedAtKST.getSeconds()).padStart(2, "0");

          const koreanTimeString = `${year}-${month}-${day} ${hour}:${minute}:${second}`;

          console.log(koreanTimeString);

          result.innerHTML = `
              <div id='health_info' data-care-id="${i.care_id}" class="card-hover bg-gradient-to-br from-yellow-50 to-orange-50 rounded-xl p-6 border border-yellow-200">
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
                                        <div class="text-2xl font-bold text-gray-800">${i.weight_kg ? i.weight_kg + 'kg' : '정보없음'}</div>
                                        <div class="text-sm text-gray-600">체중</div>
                                    </div>
                                    <div class="text-center">
                                        <div class="text-2xl font-bold text-gray-800">${i.water ? i.water + 'ml' : '정보없음'}</div>
                                        <div class="text-sm text-gray-600">수분 섭취</div>
                                    </div>
                                    <div class="text-center">
                                        <div class="text-2xl font-bold text-gray-800">${i.food ? i.food + 'g' : '정보없음'}</div>
                                        <div class="text-sm text-gray-600">사료량</div>
                                    </div>
                                    <div class="text-center">
                                        <div class="text-2xl font-bold text-gray-800">${i.walk_time_minutes ? i.walk_time_minutes + '분' : '정보없음'}</div>
                                        <div class="text-sm text-gray-600">산책 시간</div>
                                    </div>
                                </div>
                                
                                <div class="pt-4 border-t border-yellow-200">
                                    <div class="flex justify-between items-center mb-2">
                                        <span class="text-sm text-gray-500">배변 상태</span>
                                        <span class="bg-green-100 text-green-800 px-3 py-1 rounded-full text-sm font-medium">
                                            <i class="fas fa-check-circle mr-1"></i>${i.excrement_status || '정보없음'}
                                        </span>
                                    </div>
                                    <div class="flex justify-between items-center">
                                        <span class="text-sm text-gray-500">기록 일시</span>
                                        <span class="text-sm text-gray-600">${koreanTimeString}</span>
                                    </div>
                                </div>
                            </div>
                           
            `;
          history.appendChild(result);
        });

    }
}

