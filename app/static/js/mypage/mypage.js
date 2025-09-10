document.addEventListener('DOMContentLoaded', function() {
    // 모달 관련 요소들
    const addPetBtn = document.getElementById('add-pet-btn');
    const petModal = document.getElementById('add-pet-modal');
    const closePetModal = document.getElementById('close-pet-modal');
    const cancelPetForm = document.getElementById('cancel-pet-form');
    
    let personaModal = null;
    let closePersonaModal = null;
    let cancelPersonaForm = null;

    // 프로필 모달 관련 요소들
    const viewPetModal = document.getElementById('view-pet-modal');
    const closeProfileModal = document.getElementById('close-profile-modal');
    const createPersonaBtn = document.getElementById('create-persona-btn');
    const editPetBtn = document.getElementById('edit-pet-btn');
    const deletePetBtn = document.getElementById('delete-pet-btn');

    const petSpecies = document.getElementById('pet_species')
    const petBreed = document.getElementById('pet_breed')

    const addPetForm = document.getElementById('add-pet-form')
    let addPersonaForm = null;

    document.addEventListener('click', (e) => {
        if (e.target.id === 'add-pet-btn-empty'){
            showAddPetModal();
        }
    })

    // 반려동물 등록 모달 열기 및 동물 종류 데이터 가져오기
    addPetBtn.addEventListener('click', async () => {
        showAddPetModal();
    });

    
    // 반려동물 등록 모달 닫기
    [closePetModal, cancelPetForm].forEach(btn => {
        btn.addEventListener('click', () => {
            petModal.classList.add('hidden');
        });
    });
    
    // 페르소나 모달 닫기 (동적 생성 시 이벤트 처리)
    
    // 프로필 모달 닫기
    closeProfileModal.addEventListener('click', () => {
        viewPetModal.classList.add('hidden');
    });
    
    // 반려동물 등록 모달 열어서 수정
    editPetBtn.addEventListener('click', (e) => {
        console.log(e.target.dataset.currentPetInfo)
        const petInfo = JSON.parse(e.target.dataset.currentPetInfo)

        viewPetModal.classList.add('hidden')
        showAddPetModal(petInfo)
    })

    // 반려동물 삭제
    deletePetBtn.addEventListener('click', async (e) => {
        //
        const pet = e.target.closest('[data-current-pet-id]')
        const petId = pet.dataset.currentPetId
        console.log(petId)

        const response = await fetch(`/api/delete-pet/${petId}`,
           {method: 'DELETE'}
        )
        const data = await response.json()

        console.log(data.message)
        // 모달 닫고 새로고침
        viewPetModal.classList.add('hidden')
        getPetInfo()
    })

    // 프로필 모달에서 페르소나 생성 버튼 클릭
    createPersonaBtn.addEventListener('click', async (e) => {  
        // dataset의 데이터에 따라 페르소나 생성 또는 수정으로 분기
        const mode = e.currentTarget.dataset.mode
        let personaData;
        if (mode === 'edit') {
            personaData = JSON.parse(e.currentTarget.dataset.persona)
        } else {
            personaData = null;
        }

        const petProfile = e.target.closest('[data-current-pet-id]')
        const petId = petProfile.dataset.currentPetId
        console.log(petId)

        // 페르소나 모달을 동적으로 생성
        await createPersonaModal();
        
        // 모달 관련 변수들을 다시 할당
        personaModal = document.getElementById('add-persona-modal');
        closePersonaModal = document.getElementById('close-persona-modal');
        cancelPersonaForm = document.getElementById('cancel-persona-form');
        addPersonaForm = document.getElementById('add-persona-form');
        
        // 이벤트 리스너 설정
        setupPersonaModalEvents(mode, petId, personaData);
        
        viewPetModal.classList.add('hidden');
        personaModal.classList.remove('hidden');
        personaModal.querySelector('.bg-white').classList.add('modal-enter');
        
        // 선택된 펫 이름을 페르소나 모달에 표시
        const petName = document.getElementById('profile-pet-name').textContent;
        document.getElementById('selected-pet-name').textContent = petName;
        
        // 페르소나 모달 데이터 로드
        await loadPersonaData();
        
        // 존댓말/반말 태그 클릭 효과 등록
        setupPolitenessTagEvents();

        // 페르소나 수정인 경우 데이터 채우기
        if (mode === 'edit') {
            populatePersonaData(personaData);
        }
    });

    // 모달 외부 클릭시 닫기 (반려동물 등록, 프로필 모달)
    [petModal, viewPetModal].forEach(modal => {
        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                modal.classList.add('hidden');
            }
        });
    });

    petSpecies.addEventListener('change', async (e) => {
        const species_id = e.target.value
        console.log(species_id)
        const response = await fetch(`/api/breeds/${species_id}`)
        const data = await response.json()
        
        petBreed.innerHTML = ''
        const opt = document.createElement('option')
        opt.textContent = '품종을 선택하세요.'
        petBreed.appendChild(opt)
        
        data.data.forEach((breed) => {
            // console.log(breed)
            const opt = document.createElement('option')
            opt.textContent = breed.breed_name
            opt.value = breed.breed_id
            petBreed.appendChild(opt)
        })
    })

    addPetForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const formData = new FormData(e.target);

        // 

        if (!formData.has('is_neutered')) {
            formData.append('is_neutered', 'false');
        } else {
            formData.set('is_neutered', 'true')
        }

        console.log('보낼 데이터:', formData);

        const saveBtn = document.getElementById('save-pet-btn')
        let response;

        if (saveBtn.dataset.mode === 'add') {
            response = await fetch('/api/add-pet/', {
                method: 'POST',
                body: formData
            })
        } else {
            response = await fetch(`/api/update-pet/${saveBtn.dataset.petId}`, {
                method: 'PUT',
                body: formData
            })
        }
        const data = await response.json()
        if (data.success) {
            // 모달 닫기
            petModal.classList.add('hidden');
            // 펫 목록 새로고침 또는 동적 추가
            getPetInfo();
        }
        // 폼 리셋
        e.target.reset();
    })


    // 기존 성격 태그 클릭 효과는 동적 렌더링에서 처리됩니다

    // 이벤트 위임을 사용한 펫 카드 클릭 처리
    document.getElementById('pet-profile-grid').addEventListener('click', async (e) => {
        const petCard = e.target.closest('[data-pet-id]')
        if (petCard && petCard.dataset.petId) {
            const petId = petCard.dataset.petId
            try {
                const response = await fetch(`/api/pet-profile/${petId}`)
                
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                
                const petData = await response.json()
                showPetProfile(petData)
            } catch (error) {
                console.error('펫 프로필 로딩 실패:', error)
                console.error('Response details:', error.message)
            }
        }
    })

    getPetInfo()
    getUserProfile()
});

// 페르소나 모달 동적 생성 함수
function createPersonaModal() {
    // 기존 모달이 있다면 제거
    const existingModal = document.getElementById('add-persona-modal');
    if (existingModal) {
        existingModal.remove();
    }

    const modalHTML = `
    <!-- 페르소나 생성 모달 -->
    <div id="add-persona-modal" class="fixed inset-0 bg-black bg-opacity-50 z-50 hidden flex items-center justify-center">
        <div class="bg-white rounded-xl shadow-2xl max-w-4xl w-full mx-4 max-h-[90vh] overflow-y-auto">
            <div class="p-6 border-b border-gray-200 bg-gradient-to-r from-primary-500 to-secondary-500 text-white rounded-t-xl">
                <div class="flex justify-between items-center">
                    <h2 class="text-xl font-bold">
                        <i class="fas fa-magic mr-2"></i>
                        페르소나 - <span id="selected-pet-name">반려동물</span>
                    </h2>
                    <button id="close-persona-modal" class="text-white hover:text-gray-300 transition-colors">
                        <i class="fas fa-times text-xl"></i>
                    </button>
                </div>
            </div>
            
            <div class="p-6">
                <form id="add-persona-form" class="space-y-8" method="POST">
                    <!-- 호칭 설정 -->
                    <div class="bg-gray-50 p-6 rounded-xl">
                        <h3 class="text-lg font-semibold text-gray-800 mb-4">
                            <i class="fas fa-user text-primary-500 mr-2"></i>
                            호칭 설정
                        </h3>
                        <div class="form-group">
                            <label for="user_call" class="block text-sm font-medium text-gray-700 mb-2">
                                사용자를 부르는 호칭 <span class="text-red-500">*</span>
                            </label>
                            <input type="text" name="user_call" id="user_call" required
                                   class="w-full p-3 border-2 border-gray-200 rounded-lg focus:border-primary-500 focus:ring-2 focus:ring-primary-200 transition-all"
                                   placeholder="예: 엄마, 아빠, 주인">
                        </div>
                    </div>

                    <!-- 말투 설정 -->
                    <div class="bg-gray-50 p-6 rounded-xl">
                        <h3 class="text-lg font-semibold text-gray-800 mb-4">
                            <i class="fas fa-comment text-primary-500 mr-2"></i>
                            말투 설정
                        </h3>
                        
                        <!-- 존댓말/반말 -->
                        <div class="mb-6">
                            <label class="block text-sm font-medium text-gray-700 mb-3">존댓말/반말 <span class="text-red-500">*</span></label>
                            <div class="flex gap-3">
                                <label class="politeness-tag">
                                    <input type="radio" name="politeness" value="formal" class="hidden">
                                    <span class="block px-4 py-2 text-center bg-white border-2 border-primary-500 text-primary-500 rounded-lg cursor-pointer hover:bg-primary-50 transition-all">존댓말</span>
                                </label>
                                <label class="politeness-tag">
                                    <input type="radio" name="politeness" value="informal" class="hidden">
                                    <span class="block px-4 py-2 text-center bg-white border-2 border-primary-500 text-primary-500 rounded-lg cursor-pointer hover:bg-primary-50 transition-all">반말</span>
                                </label>
                            </div>
                        </div>

                        <!-- 말투 스타일 -->
                        <div class="mb-6">
                            <label class="block text-sm font-medium text-gray-700 mb-3">말투 스타일 <span class="text-red-500">*</span> (한 개 선택)</label>
                            <div id="speech-styles-container" class="flex flex-wrap gap-2">
                                <!-- 말투 스타일들이 동적으로 렌더링됩니다 -->
                            </div>
                        </div>

                        <div class="mt-4">
                            <label for="speech_habit" class="block text-sm font-medium text-gray-700 mb-2">
                                특별한 말버릇
                            </label>
                            <input type="text" name="speech_habit" id="speech_habit"
                                   class="w-full p-3 border-2 border-gray-200 rounded-lg focus:border-primary-500 focus:ring-2 focus:ring-primary-200 transition-all"
                                   placeholder="예: 끝에 ~냥 붙이기, 말끝을 '~멍'으로 끝내기">
                        </div>
                    </div>

                    <!-- 성격 설정 -->
                    <div class="bg-gray-50 p-6 rounded-xl">
                        <h3 class="text-lg font-semibold text-gray-800 mb-4">
                            <i class="fas fa-heart text-primary-500 mr-2"></i>
                            성격 및 특징 <span class="text-red-500">*</span> (여러 개 선택 가능)
                        </h3>
                        
                        <div id="personality-traits-container">
                            <!-- 성격 특성들이 동적으로 렌더링됩니다 -->
                        </div>
                    </div>

                    <!-- 추가 정보 -->
                    <div class="bg-gray-50 p-6 rounded-xl">
                        <h3 class="text-lg font-semibold text-gray-800 mb-4">
                            <i class="fas fa-info-circle text-primary-500 mr-2"></i>
                            추가 정보
                        </h3>
                        
                        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                            <div class="form-group">
                                <label for="likes" class="block text-sm font-medium text-gray-700 mb-2">
                                    <i class="fas fa-thumbs-up text-green-500 mr-1"></i>
                                    좋아하는 것
                                </label>
                                <textarea id="likes" name="likes" rows="3" 
                                          class="w-full p-3 border-2 border-gray-200 rounded-lg focus:border-primary-500 focus:ring-2 focus:ring-primary-200 transition-all resize-y"
                                          placeholder="쉼표로 구분해서 입력하세요. 예: 산책, 간식, 공놀이"></textarea>
                            </div>

                            <div class="form-group">
                                <label for="dislikes" class="block text-sm font-medium text-gray-700 mb-2">
                                    <i class="fas fa-thumbs-down text-red-500 mr-1"></i>
                                    싫어하는 것
                                </label>
                                <textarea id="dislikes" name="dislikes" rows="3"
                                          class="w-full p-3 border-2 border-gray-200 rounded-lg focus:border-primary-500 focus:ring-2 focus:ring-primary-200 transition-all resize-y"
                                          placeholder="쉼표로 구분해서 입력하세요. 예: 목욕, 큰 소리, 낯선 사람"></textarea>
                            </div>

                            <div class="form-group">
                                <label for="habits" class="block text-sm font-medium text-gray-700 mb-2">
                                    <i class="fas fa-sync text-yellow-500 mr-1"></i>
                                    습관
                                </label>
                                <textarea id="habits" name="habits" rows="3"
                                          class="w-full p-3 border-2 border-gray-200 rounded-lg focus:border-primary-500 focus:ring-2 focus:ring-primary-200 transition-all resize-y"
                                          placeholder="쉼표로 구분해서 입력하세요. 예: 꼬리 흔들기, 골골거리기"></textarea>
                            </div>

                            <div class="form-group">
                                <label for="family_info" class="block text-sm font-medium text-gray-700 mb-2">
                                    <i class="fas fa-home text-blue-500 mr-1"></i>
                                    가족 정보
                                </label>
                                <textarea id="family_info" name="family_info" rows="3"
                                          class="w-full p-3 border-2 border-gray-200 rounded-lg focus:border-primary-500 focus:ring-2 focus:ring-primary-200 transition-all resize-y"
                                          placeholder="가족 구성원, 관계 등을 입력하세요"></textarea>
                            </div>
                        </div>

                        <div class="form-group mt-4">
                            <label for="special_note" class="block text-sm font-medium text-gray-700 mb-2">
                                <i class="fas fa-star text-yellow-500 mr-1"></i>
                                특별한 사항
                            </label>
                            <textarea id="special_note" name="special_note" rows="3"
                                      class="w-full p-3 border-2 border-gray-200 rounded-lg focus:border-primary-500 focus:ring-2 focus:ring-primary-200 transition-all resize-y"
                                      placeholder="외형, 특별한 에피소드 등 대화에 반영되었으면 하는 점을 자유롭게 작성하세요"></textarea>
                        </div>
                    </div>

                    <div class="flex justify-end gap-3 pt-4 border-t border-gray-200">
                        <button type="button" id="cancel-persona-form" 
                                class="px-6 py-2 text-gray-600 bg-gray-100 rounded-lg hover:bg-gray-200 transition-all">
                            취소
                        </button>
                        <button id="save-persona-btn" type="submit"
                                class="px-6 py-2 bg-gradient-to-r from-secondary-500 to-secondary-600 text-white rounded-lg hover:from-secondary-600 hover:to-secondary-700 transition-all hover:-translate-y-0.5 shadow-md">
                            저장
                        </button>
                    </div>
                </form>
            </div>
        </div>
    </div>`;

    // body에 모달 추가
    document.body.insertAdjacentHTML('beforeend', modalHTML);
}

// 페르소나 모달 이벤트 설정 함수
function setupPersonaModalEvents(mode, petId, personaData) {
    const personaModal = document.getElementById('add-persona-modal');
    const closePersonaModal = document.getElementById('close-persona-modal');
    const cancelPersonaForm = document.getElementById('cancel-persona-form');
    const addPersonaForm = document.getElementById('add-persona-form');

    // 모달 데이터 설정
    addPersonaForm.dataset.mode = mode;
    addPersonaForm.dataset.currentPetId = petId;

    // 모달 닫기 이벤트
    const closeModal = () => {
        personaModal.classList.add('hidden');
        // 모달 제거
        setTimeout(() => {
            personaModal.remove();
        }, 300);
    };

    [closePersonaModal, cancelPersonaForm].forEach(btn => {
        btn.addEventListener('click', closeModal);
    });

    // 모달 외부 클릭시 닫기
    personaModal.addEventListener('click', (e) => {
        if (e.target === personaModal) {
            closeModal();
        }
    });

    // 폼 제출 이벤트
    addPersonaForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const formData = new FormData(e.target);
        const trimedFormData = {};

        // trait_id(체크박스)는 여러 개 선택될 수 있으므로 getAll로 배열로 받기
        trimedFormData['trait_id'] = formData.getAll('trait_id');
        
        for (let [key, value] of formData.entries()) {
            if (key !== 'trait_id' && value.trim() !== '') {
                trimedFormData[key] = value;
            }
        }

        console.log(trimedFormData);

        let response;
        if (mode === 'add') {
            response = await fetch(`/api/save-persona/${petId}`, {
                method: 'POST',
                body: JSON.stringify(trimedFormData),
                headers: {'Content-Type': 'application/json'}
            });
        } else {
            response = await fetch(`/api/update-persona/${petId}`, {
                method: 'PUT',
                body: JSON.stringify(trimedFormData),
                headers: {'Content-Type': 'application/json'}
            });
        }

        const data = await response.json();
        if (data.success) {
            // 모달 닫기
            closeModal();
            console.log(data.success);
            
            // 폼 리셋
            e.target.reset();
        }
    });
}

// 페르소나 데이터를 폼에 채우는 함수
function populatePersonaData(personaData) {
    // DOM 업데이트가 완료될 때까지 기다림
    requestAnimationFrame(() => {
        console.log(personaData);

        document.getElementById('user_call').value = personaData.user_call;

        // 존댓말 여부 라디오버튼
        const politeness = document.querySelectorAll('input[name="politeness"]');
        console.log(personaData.politeness, typeof(personaData.politeness));
        politeness.forEach(radio => {
            if (radio.value == personaData.politeness) {
                radio.checked = true;
                // 시각적 상태도 함께 업데이트
                const span = radio.closest('.politeness-tag').querySelector('span');
                span.classList.add('bg-primary-500', 'text-white');
                span.classList.remove('bg-white', 'text-primary-500');
            } else {
                radio.checked = false;
                // 다른 버튼들은 기본 상태로
                const span = radio.closest('.politeness-tag').querySelector('span');
                span.classList.remove('bg-primary-500', 'text-white');
                span.classList.add('bg-white', 'text-primary-500');
            }
        });

        // 말투 스타일
        const styles = document.querySelectorAll('input[name="style_id"]');
        styles.forEach(radio => {
            if (radio.value == personaData.style_id) {
                radio.checked = true;
                // 시각적 상태도 함께 업데이트
                const span = radio.closest('.speech-style-tag').querySelector('span');
                span.style.backgroundColor = span.dataset.bgColor;
                span.style.color = '#ffffff';
                span.style.borderColor = span.dataset.bgColor;
            } else {
                radio.checked = false;
                // 다른 버튼들은 기본 상태로
                const span = radio.closest('.speech-style-tag').querySelector('span');
                span.style.backgroundColor = '#ffffff';
                span.style.color = span.dataset.textColor;
                span.style.borderColor = span.dataset.textColor;
            }
        });

        document.getElementById('speech_habit').value = personaData.speech_habit;
        
        // 성격 특성 (체크박스)
        const traits = document.querySelectorAll('input[name="trait_id"]');
        if (personaData.traits && personaData.traits.length > 0) {
            traits.forEach(checkbox => {
                // personaData.traits 배열에서 현재 체크박스의 value와 일치하는 trait_id가 있는지 확인
                const isSelected = personaData.traits.some(trait => 
                    trait.trait_id == parseInt(checkbox.value)
                );
                
                if (isSelected) {
                    checkbox.checked = true;
                    // 시각적 상태도 함께 업데이트
                    const span = checkbox.closest('.personality-tag').querySelector('span');
                    const bgColor = span.dataset.bgColor || '#FFD43B';
                    span.style.setProperty('background-color', bgColor, 'important');
                    span.style.setProperty('color', '#ffffff', 'important');
                    span.style.setProperty('border-color', bgColor, 'important');
                } else {
                    checkbox.checked = false;
                    // 선택 해제 상태로
                    const span = checkbox.closest('.personality-tag').querySelector('span');
                    const textColor = span.dataset.textColor || '#FFD43B';
                    span.style.setProperty('background-color', '#ffffff', 'important');
                    span.style.setProperty('color', textColor, 'important');
                    span.style.setProperty('border-color', textColor, 'important');
                }
            });
        }

        document.getElementById('likes').value = personaData.likes;
        document.getElementById('dislikes').value = personaData.dislikes;
        document.getElementById('habits').value = personaData.habits;
        document.getElementById('family_info').value = personaData.family_info;
        document.getElementById('special_note').value = personaData.special_note;
    });
}


// 반려동물 등록/수정 모달창 여는 함수
async function showAddPetModal(pet=null) {
    const petModal = document.getElementById('add-pet-modal');
    const petName = document.getElementById('pet_name');
    const petSpecies = document.getElementById('pet_species')
    const petBreed = document.getElementById('pet_breed')
    const petAge = document.getElementById('pet_age')
    const petBirthDate = document.getElementById('birthdate');
    const petAdoptionDate = document.getElementById('adoption_date');
    const petGender = document.querySelectorAll('input[name="pet_gender"]');
    const isNeutered = document.getElementById('is_neutered')
    // 프로필 이미지는...?
    const saveBtn = document.getElementById('save-pet-btn')

    petModal.classList.remove('hidden');
    petModal.querySelector('.bg-white').classList.add('modal-enter');
    
    const response = await fetch('/api/species/')
    const data = await response.json()
    
    petSpecies.innerHTML = ''
    const opt = document.createElement('option')
    opt.textContent = '동물을 선택하세요.'
    petSpecies.appendChild(opt)
    
    await data.data.forEach((species) => {
        const opt = document.createElement('option')
        opt.textContent = species.species_name
        opt.value = species.species_id
        petSpecies.appendChild(opt)
    })

    // 정보 수정의 경우
    if (pet) {
        petName.value = pet.pet_name;
        petSpecies.value = pet.species_id;

        const response = await fetch(`/api/breeds/${pet.species_id}`)
        const data = await response.json()
        
        petBreed.innerHTML = ''
        await data.data.forEach((breed) => {
            // console.log(breed)
            const opt = document.createElement('option')
            opt.textContent = breed.breed_name
            opt.value = breed.breed_id
            petBreed.appendChild(opt)
        })

        petBreed.value = pet.breed_id;
        petAge.value = pet.pet_age;
        petBirthDate.value = pet.birthdate;
        petAdoptionDate.value = pet.adoption_date;

        petGender.forEach(radio => {
            radio.checked = (radio.value === pet.pet_gender);
        });
        if (pet.is_neutered) {
            isNeutered.checked = true;
        }

        saveBtn.dataset.mode = 'edit';
        saveBtn.dataset.petId = pet.pet_id;
    } else {
        saveBtn.dataset.mode = 'add'
        delete saveBtn.dataset.petId;
    }
}

// 반려동물 프로필 렌더링 (성능 최적화)
async function getPetInfo() {
    // 로딩 인디케이터 표시
    showLoadingState();
    
    try {
        const response = await fetch('/api/pets/');
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        console.log(data);
        
        
        // 비동기 렌더링으로 UI 블로킹 방지
        requestAnimationFrame(() => {
            renderPetCards(data);
            hideLoadingState();
        });
        
    } catch (error) {
        console.error('펫 정보 로딩 실패:', error);
        showErrorState();
    }
}

// 로딩 상태 표시
function showLoadingState() {
    const petProfile = document.getElementById('pet-profile-grid');
    petProfile.innerHTML = `
        <div class="col-span-full flex items-center justify-center py-12">
            <div class="text-center">
                <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-500 mx-auto mb-4"></div>
                <p class="text-gray-600">반려동물 정보를 불러오는 중...</p>
            </div>
        </div>
    `;
}

// 에러 상태 표시
function showErrorState() {
    const petProfile = document.getElementById('pet-profile-grid');
    petProfile.innerHTML = `
        <div class="col-span-full flex items-center justify-center py-12">
            <div class="text-center">
                <i class="fas fa-exclamation-triangle text-4xl text-red-500 mb-4"></i>
                <p class="text-gray-600">펫 정보를 불러오는 중 오류가 발생했습니다.</p>
                <button onclick="getPetInfo()" class="mt-4 px-4 py-2 bg-primary-500 text-white rounded-lg hover:bg-primary-600">
                    다시 시도
                </button>
            </div>
        </div>
    `;
}

// 로딩 상태 숨김
function hideLoadingState() {
    // 필요시 추가 로직
}

function renderPetCards(data) {
    const petProfile = document.getElementById('pet-profile-grid');
    
    // 빈 상태 처리
    if (!data || data.length === 0) {
        petProfile.innerHTML = `
            <div class="col-span-full flex items-center justify-center py-12">
                <div class="text-center">
                    <i class="fas fa-heart text-6xl text-gray-300 mb-4"></i>
                    <h3 class="text-xl font-semibold text-gray-600 mb-2">등록된 반려동물이 없습니다</h3>
                    <p class="text-gray-500 mb-6">새로운 반려동물을 등록해보세요!</p>
                    <button id="add-pet-btn-empty" class="px-6 py-3 bg-primary-500 text-white rounded-lg hover:bg-primary-600">
                        반려동물 등록하기
                    </button>
                </div>
            </div>
        `;
        return;
    }
    
    // DocumentFragment 사용으로 DOM 조작 최적화
    const fragment = document.createDocumentFragment();
    
    // 배치 처리로 렌더링 최적화
    data.forEach((pet, index) => {
        const petCard = createPetCard(pet);
        fragment.appendChild(petCard);
    });
    
    // 한 번에 DOM에 추가
    petProfile.innerHTML = '';
    petProfile.appendChild(fragment);
}

// 펫 카드 생성 함수 (재사용성 개선)
function createPetCard(pet) {
    const div1 = document.createElement('div');
    div1.className = "bg-white rounded-xl shadow-lg p-6 text-center hover:shadow-xl transition-all cursor-pointer transform hover:scale-105";
    div1.dataset.petId = pet.pet_id;
    
    // 프로필 이미지/아이콘
    const avatarDiv = document.createElement('div');
    avatarDiv.className = "w-16 h-16 bg-gradient-to-r from-primary-100 to-secondary-100 rounded-full mx-auto mb-4 flex items-center justify-center";
    
    if (pet.profile_image_url && pet.profile_image_url.trim() !== '') {
        const img = document.createElement('img');
        img.src = pet.profile_image_url;
        img.alt = "";
        img.className = "w-full h-full rounded-full object-cover";
        img.loading = "lazy";
        
        // 이미지 로드 실패 시 발바닥 아이콘으로 대체
        img.onerror = function() {
            avatarDiv.innerHTML = '<i class="fa-solid fa-paw fa-2xl" style="color: #FFD43B"></i>';
        };
        
        avatarDiv.appendChild(img);
    } else {
        avatarDiv.innerHTML = '<i class="fa-solid fa-paw fa-2xl" style="color: #FFD43B"></i>';
    }
    
    // 펫 정보
    const nameP = document.createElement('p');
    nameP.textContent = pet.pet_name;
    nameP.className = "text-gray-700 font-medium mb-1";
    
    const speciesP = document.createElement('p');
    speciesP.textContent = pet.species_name || '알 수 없음';
    speciesP.className = "text-sm text-gray-500";
    
    // 추가 정보 (나이, 품종)
    if (pet.pet_age || pet.breed_name) {
        const infoP = document.createElement('p');
        const ageText = pet.pet_age ? `${pet.pet_age}살` : '';
        const breedText = pet.breed_name || '';
        const separator = ageText && breedText ? ' · ' : '';
        infoP.textContent = ageText + separator + breedText;
        infoP.className = "text-xs text-gray-400 mt-1";
        
        div1.append(avatarDiv, nameP, speciesP, infoP);
    } else {
        div1.append(avatarDiv, nameP, speciesP);
    }
    
    return div1;
}

// 반려동물 프로필 모달 표시
async function showPetProfile(pet) {
    console.log('프로필에 표시될 펫 정보 : ', pet)
    const viewPetModal = document.getElementById('view-pet-modal')
    
    // 프로필 정보 업데이트
    document.getElementById('profile-pet-name').textContent = pet.pet_name
    document.getElementById('profile-pet-display-name').textContent = pet.pet_name
    
    // 프로필 이미지
    const profileImage = document.getElementById('profile-pet-image')
    const profileIcon = document.getElementById('profile-pet-icon')

    if (pet.profile_image_url && pet.profile_image_url.trim() !== '') {
        profileImage.src = pet.profile_image_url
        profileImage.classList.remove('hidden')
        profileIcon.classList.add('hidden')
    } else {
        profileImage.classList.add('hidden')
        profileIcon.classList.remove('hidden')
    }
    
    // 기본 정보
    document.getElementById('profile-species').textContent = pet.species_name || '-'
    document.getElementById('profile-breed').textContent = pet.breed_name || '-'
    document.getElementById('profile-age').textContent = pet.pet_age ? pet.pet_age + '살' : '-'
    document.getElementById('profile-gender').textContent = pet.pet_gender || '-'
    
    // 날짜 정보
    document.getElementById('profile-birthdate').textContent = pet.birthdate || '-'
    document.getElementById('profile-adoption-date').textContent = pet.adoption_date || '-'
    document.getElementById('profile-neutered').textContent = pet.is_neutered ? '완료' : '미완료'
    
    // 페르소나 상태 (향후 확장)
    const data = await getPersonaInfo(pet.pet_id)
    renderPersona(data)    
    
    // 현재 선택된 펫 ID 저장 (추후 사용)
    viewPetModal.dataset.currentPetId = pet.pet_id

    const editBtn = document.getElementById('edit-pet-btn')
    editBtn.dataset.currentPetInfo = JSON.stringify(pet)
    
    // 모달 표시
    viewPetModal.classList.remove('hidden')
    viewPetModal.querySelector('.bg-white').classList.add('modal-enter')
}

// 페르소나 정보 가져오기
async function getPersonaInfo(petId) {
    const response = await fetch(`/api/get-persona/${petId}`)
    const data = await response.json()
    console.log('페르소나 정보 : ', data)
    return data
}

// 페르소나 정보 렌더링
function renderPersona(data) {
    const personaStatus = document.getElementById('persona-status')
    personaStatus.innerHTML = ''
    
    if (data.message) {
        // 페르소나 없는 경우
        personaStatus.innerHTML = `
            <div class="text-center py-4">
                <i class="fas fa-robot text-3xl text-gray-400 mb-2"></i>
                <p class="text-gray-600">${data.message}</p>
            </div>
        `
        // 페르소나 생성 버튼으로 토글
        toggleCreatePersonaBtn()
        
    } else {
        // 페르소나가 있는 경우
        const persona = data.pet_persona
        const traits = persona.traits
        
        const container = document.createElement('div')
        container.className = 'space-y-4'
        
        // 페르소나 기본 정보
        const infoSection = document.createElement('div')
        infoSection.className = 'bg-white p-4 rounded-lg border border-gray-200'
        
        const infoTitle = document.createElement('h5')
        infoTitle.className = 'font-semibold text-gray-700 mb-3 flex items-center'
        infoTitle.innerHTML = '<i class="fas fa-user-circle text-primary-500 mr-2"></i>페르소나 정보'
        infoSection.appendChild(infoTitle)
        
        // 정보 그리드
        const infoGrid = document.createElement('div')
        infoGrid.className = 'grid grid-cols-1 gap-2 text-sm'
        
        // 유용한 정보만 표시
        const displayInfo = {
            'user_call': '호칭',
            'politeness': '말투',
            'speech_habit': '말버릇',
            'likes': '좋아하는 것',
            'dislikes': '싫어하는 것',
            'habits': '습관',
            'family_info': '가족 정보',
            'special_note': '특별한 사항'
        }
        
        for (const [key, label] of Object.entries(displayInfo)) {
            let value = persona[key]
            if (value && value !== '' && value !== null && value !== 'undefined') {
                // 말투 표시 변환
                if (key === 'politeness') {
                    value = value === 'formal' ? '존댓말' : '반말'
                }
                
                const infoRow = document.createElement('div')
                infoRow.className = 'flex justify-between items-start py-1'
                infoRow.innerHTML = `
                    <span class="text-gray-600 font-medium min-w-[80px]">${label}:</span>
                    <span class="text-gray-800 text-right flex-1 ml-2">${value}</span>
                    `
                    infoGrid.appendChild(infoRow)
                }
            }
            
        infoSection.appendChild(infoGrid)
        container.appendChild(infoSection)
        
        // 성격 특성 섹션
        if (traits && traits.length > 0) {
            const traitsSection = document.createElement('div')
            traitsSection.className = 'bg-white p-4 rounded-lg border border-gray-200'
            
            const traitsTitle = document.createElement('h5')
            traitsTitle.className = 'font-semibold text-gray-700 mb-3 flex items-center'
            traitsTitle.innerHTML = '<i class="fas fa-heart text-primary-500 mr-2"></i>성격 및 특징'
            traitsSection.appendChild(traitsTitle)
            
            const traitsContainer = document.createElement('div')
            traitsContainer.className = 'flex flex-wrap gap-2'
            
            traits.forEach(trait => {
                console.log('확인용 : ', trait)
                const tag = document.createElement('span')
                tag.className = 'inline-block px-3 py-1 bg-primary-100 text-primary-700 rounded-full text-sm font-medium'
                tag.textContent = trait.trait_name
                traitsContainer.appendChild(tag)
            })
            
            traitsSection.appendChild(traitsContainer)
            container.appendChild(traitsSection)
        }
        
        // 상태 표시
        const statusBadge = document.createElement('div')
        statusBadge.className = 'text-center'
        statusBadge.innerHTML = `
        <span class="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-green-100 text-green-800">
        <i class="fas fa-check-circle mr-2"></i>
        페르소나 생성 완료
        </span>
        `
        container.appendChild(statusBadge)
        
        personaStatus.appendChild(container)

        // 페르소나 수정 버튼으로 토글
        toggleCreatePersonaBtn(persona)
        
    }
}

function toggleCreatePersonaBtn(persona=null) {
    const createPersonaBtn = document.getElementById('create-persona-btn')
    const personaBtnText = document.getElementById('persona-btn-text')

    if (!persona) {
        // 페르소나 없는 경우 - 추가
        createPersonaBtn.dataset.mode = 'add';
        delete createPersonaBtn.dataset.persona;
        personaBtnText.textContent = '페르소나 생성';
        
    } else {
        // 페르소나 있는 경우 - 수정
        createPersonaBtn.dataset.mode = 'edit';
        createPersonaBtn.dataset.persona = JSON.stringify(persona);
        personaBtnText.textContent = '페르소나 수정';

    }
}

// 페르소나 생성 모달 데이터 로드
async function loadPersonaData() {
    try {
        // 말투 스타일과 성격 특성을 병렬로 가져오기
        const [speechStylesResponse, personalityTraitsResponse] = await Promise.all([
            fetch('/api/speech-styles/'),
            fetch('/api/personality-traits')
        ]);

        const speechStyles = await speechStylesResponse.json();
        const personalityTraits = await personalityTraitsResponse.json();

        // 말투 스타일 렌더링
        renderSpeechStyles(speechStyles);
        
        // 성격 특성 렌더링
        renderPersonalityTraits(personalityTraits);

    } catch (error) {
        console.error('페르소나 데이터 로딩 실패:', error);
    }
}

// 말투 스타일 렌더링 (태그 형식)
function renderSpeechStyles(speechStyles) {
    const container = document.getElementById('speech-styles-container');
    container.innerHTML = '';

    // 말투 스타일 통일 색상 (청록색)
    const speechStyleColor = {
        borderColor: '#06b6d4', // cyan-500
        textColor: '#06b6d4',
        bgColor: '#06b6d4'
    };

    speechStyles.forEach((style, index) => {
        const label = document.createElement('label');
        label.className = 'speech-style-tag';
        
        const colors = speechStyleColor;
        
        const span = document.createElement('span');
        span.className = 'inline-block px-3 py-2 text-center bg-white border-2 rounded-lg text-sm cursor-pointer transition-all whitespace-nowrap';
        span.textContent = style.style_name;
        span.style.borderColor = colors.borderColor;
        span.style.color = colors.textColor;
        span.dataset.bgColor = colors.bgColor;
        span.dataset.textColor = colors.textColor;
        
        const input = document.createElement('input');
        input.type = 'radio';
        input.name = 'style_id';
        input.value = style.style_id;
        input.className = 'hidden';
        
        label.appendChild(input);
        label.appendChild(span);
        container.appendChild(label);
    });
    
    // 말투 스타일 태그 클릭 효과 등록
    document.querySelectorAll('.speech-style-tag').forEach(tag => {
        tag.addEventListener('click', function() {
            // 다른 모든 말투 스타일 태그 비활성화
            document.querySelectorAll('.speech-style-tag span').forEach(span => {
                span.style.backgroundColor = '#ffffff';
                span.style.color = span.dataset.textColor;
                span.style.borderColor = span.dataset.textColor;
            });
            
            // 선택된 태그만 활성화
            const radio = this.querySelector('input[type="radio"]');
            const span = this.querySelector('span');
            
            radio.checked = true;
            span.style.backgroundColor = span.dataset.bgColor;
            span.style.color = '#ffffff';
            span.style.borderColor = span.dataset.bgColor;
        });
    });
}

// 성격 특성 렌더링
function renderPersonalityTraits(personalityTraits) {
    const container = document.getElementById('personality-traits-container');
    container.innerHTML = '';

    // 카테고리별 색상 배열 (순서대로 할당)
    const categoryColorList = [
        {
            borderColor: '#ef4444', // red-500
            textColor: '#ef4444',
            bgColor: '#ef4444',
            name: '활동성 & 에너지'
        },
        {
            borderColor: '#3b82f6', // blue-500
            textColor: '#3b82f6',
            bgColor: '#3b82f6',
            name: '사회성 & 친화력'
        },
        {
            borderColor: '#22c55e', // green-500
            textColor: '#22c55e',
            bgColor: '#22c55e',
            name: '감정 표현'
        },
        {
            borderColor: '#a855f7', // purple-500
            textColor: '#a855f7',
            bgColor: '#a855f7',
            name: '학습 & 적응력'
        },
        {
            borderColor: '#eab308', // yellow-500
            textColor: '#eab308',
            bgColor: '#eab308',
            name: '특별한 특징'
        }
    ];

    Object.keys(personalityTraits).forEach((category, index) => {
        const traits = personalityTraits[category];
        // console.log('카테고리:', category); // 실제 카테고리 이름 확인
        
        // 인덱스 기반으로 색상 할당
        const colors = categoryColorList[index % categoryColorList.length];
        
        const categoryDiv = document.createElement('div');
        categoryDiv.className = 'mb-6';
        
        categoryDiv.innerHTML = `
            <h4 class="text-md font-medium text-gray-700 mb-3">${category}</h4>
            <div class="flex flex-wrap gap-2" id="traits-${category}">
            </div>
        `;
        
        container.appendChild(categoryDiv);
        
        const traitsGrid = document.getElementById(`traits-${category}`);
        
        traits.forEach(trait => {
            const label = document.createElement('label');
            label.className = 'personality-tag';
            
            const span = document.createElement('span');
            span.className = 'inline-block px-3 py-2 text-center bg-white border-2 rounded-lg text-sm cursor-pointer transition-all whitespace-nowrap';
            span.textContent = trait.trait_name;
            span.style.borderColor = colors.borderColor;
            span.style.color = colors.textColor;
            span.dataset.bgColor = colors.bgColor;
            span.dataset.textColor = colors.textColor;
            span.dataset.borderColor = colors.borderColor;
            
            // console.log(`태그 "${trait.trait_name}" 색상:`, colors); // 디버깅용
            
            const input = document.createElement('input');
            input.type = 'checkbox';
            input.name = 'trait_id';
            input.value = trait.trait_id;
            input.className = 'hidden';
            
            label.appendChild(input);
            label.appendChild(span);
            traitsGrid.appendChild(label);
        });
    });
    
    // 성격 태그 클릭 효과 재등록
    document.querySelectorAll('.personality-tag').forEach(tag => {
        tag.addEventListener('click', function() {
            const checkbox = this.querySelector('input[type="checkbox"]');
            const span = this.querySelector('span');
            
            checkbox.checked = !checkbox.checked;
            
            if (checkbox.checked) {
                // 선택된 상태: 해당 카테고리 색상의 배경으로 변경
                const bgColor = span.dataset.bgColor || '#FFD43B'; // 기본값
                
                // 기존 클래스 모두 제거
                span.className = 'inline-block px-3 py-2 text-center border-2 rounded-lg text-sm cursor-pointer transition-all whitespace-nowrap';
                
                // 인라인 스타일 적용 (!important 강제)
                span.style.setProperty('background-color', bgColor, 'important');
                span.style.setProperty('color', '#ffffff', 'important');
                span.style.setProperty('border-color', bgColor, 'important');
                console.log('선택 상태로 변경됨, 배경색:', bgColor);
            } else {
                // 선택 해제된 상태: 원래 색상으로 복원
                const textColor = span.dataset.textColor || '#FFD43B'; // 기본값
                
                // 기존 클래스 모두 제거
                span.className = 'inline-block px-3 py-2 text-center border-2 rounded-lg text-sm cursor-pointer transition-all whitespace-nowrap';
                
                // 인라인 스타일 적용 (!important 강제)
                span.style.setProperty('background-color', '#ffffff', 'important');
                span.style.setProperty('color', textColor, 'important');
                span.style.setProperty('border-color', textColor, 'important');
                // console.log('선택 해제 상태로 변경됨, 텍스트색:', textColor);
            }
        });
    });
}

// 존댓말/반말 태그 클릭 효과 설정
function setupPolitenessTagEvents() {
    document.querySelectorAll('.politeness-tag').forEach(tag => {
        tag.addEventListener('click', function() {
            // 다른 모든 존댓말/반말 태그 비활성화
            document.querySelectorAll('.politeness-tag span').forEach(span => {
                span.classList.remove('bg-primary-500', 'text-white');
                span.classList.add('bg-white', 'text-primary-500');
            });
            
            // 선택된 태그만 활성화
            const radio = this.querySelector('input[type="radio"]');
            const span = this.querySelector('span');
            
            radio.checked = true;
            span.classList.add('bg-primary-500', 'text-white');
            span.classList.remove('bg-white', 'text-primary-500');
        });
    });
}

async function getUserProfile() {
    const response = await fetch('/api/user-profile/')
    const data = await response.json()
    console.log(data.user)

    const userNickname = document.getElementById('nickname')
    const userEmail = document.getElementById('email')
    userNickname.textContent = data.user.profile.nickname
    userEmail.textContent = data.user.email
}