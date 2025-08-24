document.addEventListener('DOMContentLoaded', function() {
    // 모달 관련 요소들
    const addPetBtn = document.getElementById('add-pet-btn');
    const petModal = document.getElementById('add-pet-modal');
    const closePetModal = document.getElementById('close-pet-modal');
    const cancelPetForm = document.getElementById('cancel-pet-form');
    
    const personaModal = document.getElementById('add-persona-modal');
    const closePersonaModal = document.getElementById('close-persona-modal');
    const cancelPersonaForm = document.getElementById('cancel-persona-form');

    // 프로필 모달 관련 요소들
    const viewPetModal = document.getElementById('view-pet-modal');
    const closeProfileModal = document.getElementById('close-profile-modal');
    const createPersonaBtn = document.getElementById('create-persona-btn');
    const editPetBtn = document.getElementById('edit-pet-btn');
    const deletePetBtn = document.getElementById('delete-pet-btn');

    const petSpecies = document.getElementById('pet_species')
    const petBreed = document.getElementById('pet_breed')

    const addPetForm = document.getElementById('add-pet-form')
    const addPersonaForm = document.getElementById('add-persona-modal')

    // 반려동물 등록 모달 열기 및 동물 종류 데이터 가져오기
    addPetBtn.addEventListener('click', async () => {
        petModal.classList.remove('hidden');
        petModal.querySelector('.bg-white').classList.add('modal-enter');
        
        const response = await fetch('/api/species/')
        const data = await response.json()
        
        petSpecies.innerHTML = ''
        const opt = document.createElement('option')
        opt.textContent = '동물을 선택하세요.'
        petSpecies.appendChild(opt)
        
        data.data.forEach((species) => {
            const opt = document.createElement('option')
            opt.textContent = species.species_name
            opt.value = species.species_id
            petSpecies.appendChild(opt)
        })
    });
    
    // 반려동물 등록 모달 닫기
    [closePetModal, cancelPetForm].forEach(btn => {
        btn.addEventListener('click', () => {
            petModal.classList.add('hidden');
        });
    });
    
    // 페르소나 모달 닫기
    [closePersonaModal, cancelPersonaForm].forEach(btn => {
        btn.addEventListener('click', () => {
            personaModal.classList.add('hidden');
        });
    });
    
    // 프로필 모달 닫기
    closeProfileModal.addEventListener('click', () => {
        viewPetModal.classList.add('hidden');
    });
    
    // 페르소나 모달 열기??????
    // 프로필 모달에서 페르소나 생성 버튼 클릭
    createPersonaBtn.addEventListener('click', async (e) => {
        
        const petModal = e.target.closest('[data-current-pet-id]') // 펫 프로필 모달창... 여기서 펫 아이디 가져와야할 듯.
        console.log(petModal.dataset.currentPetId)
        addPersonaForm.dataset.currentPetId = petModal.dataset.currentPetId
        console.log(addPersonaForm)

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
    });

    // 모달 외부 클릭시 닫기
    [petModal, personaModal, viewPetModal].forEach(modal => {
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
        const trimedFormData = {}

        for (let [key, value] of formData.entries()) {
            if (key === 'is_neutered') {
                trimedFormData[key] = true;
            }
            else if (value.trim() !== '') {
                trimedFormData[key] = value;
            }
        }
    
        if (!formData.has('is_neutered')) {
            trimedFormData['is_neutered'] = false;
        }

        console.log('보낼 데이터:', trimedFormData);

        const response = await fetch('/api/add-pet/', {
            method: 'POST',
            body: JSON.stringify(trimedFormData),
            headers: {'Content-Type': 'application/json'}
        })
        const data = await response.json()
        if (data.success) {
            // 모달 닫기
            petModal.classList.add('hidden');
            // 펫 목록 새로고침 또는 동적 추가
            getPetInfo()
            
            // 폼 리셋
            e.target.reset()
        }

    })
    
    addPersonaForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        console.log(addPersonaForm.dataset.currentPetId)
        const petId = addPersonaForm.dataset.currentPetId

        const formData = new FormData(e.target);
        const trimedFormData = {}

        // trait_id(체크박스)는 여러 개 선택될 수 있으므로 getAll로 배열로 받기
        trimedFormData['trait_id'] = formData.getAll('trait_id');
        
        for (let [key, value] of formData.entries()) {
            if (key !== 'trait_id' && value.trim() !== '') {
                trimedFormData[key] = value;
            }
        }

        console.log(trimedFormData)

        const response = await fetch(`/api/save-persona/${petId}`,{
            method: 'POST',
            body: JSON.stringify(trimedFormData),
            headers: {'Content-Type': 'application/json'}
        }
        )
        const data = await response.json()
                if (data.success) {
            // 모달 닫기
            personaModal.classList.add('hidden');
            
            // 폼 리셋
            e.target.reset()
        }








    })

    // 기존 성격 태그 클릭 효과는 동적 렌더링에서 처리됩니다

    // 이벤트 위임을 사용한 펫 카드 클릭 처리
    document.getElementById('pet-profile-grid').addEventListener('click', async (e) => {
        const petCard = e.target.closest('[data-pet-id]')
        if (petCard && petCard.dataset.petId) {
            const petId = petCard.dataset.petId
            try {
                const response = await fetch(`/api/pet-profile/${petId}`)
                const petData = await response.json()
                showPetProfile(petData)
            } catch (error) {
                console.error('펫 프로필 로딩 실패:', error)
            }
        }
    })

    getPetInfo()

});


// 반려동물 프로필 렌더링
async function getPetInfo() {
    const response = await fetch('/api/pets')
    const data = await response.json()

    console.log(data)
    renderPetsProfile(data)
    
}

function renderPetsProfile(data) {
    const petProfile = document.getElementById('pet-profile-grid')
    petProfile.innerHTML = ''
    
    for (let pet of data) {
        // console.log(pet)

        const div1 = document.createElement('div')
        div1.className = "bg-white rounded-xl shadow-lg p-6 text-center hover:shadow-xl transition-all cursor-pointer"
        div1.dataset.petId = pet.pet_id
        
        // 프로필 이미지/아이콘
        const div2 = document.createElement('div')
        div2.className = "w-16 h-16 bg-gradient-to-r from-primary-100 to-secondary-100 rounded-full mx-auto mb-4 flex items-center justify-center"
        
        if (pet.profile_image_url && pet.profile_image_url.trim() !== '') {
            const img = document.createElement('img')
            img.src = pet.profile_image_url
            img.alt = pet.pet_name + ' 프로필'
            img.className = "w-full h-full rounded-full object-cover"
            div2.appendChild(img)
        } else {
            const icon = document.createElement('i')
            icon.className = "fa-solid fa-paw fa-2xl"
            icon.style.color = "#FFD43B"
            div2.appendChild(icon)
        }
        div1.appendChild(div2)

        const p = document.createElement('p')
        p.textContent = pet.pet_name
        p.className = "text-gray-700 font-medium"
        div1.appendChild(p)

        const p2 = document.createElement('p')
        p2.textContent = `${pet.species_name || '알 수 없음'}`
        p2.className = "text-sm text-gray-500"
        div1.appendChild(p2)

        // 클릭 이벤트는 이벤트 위임으로 처리

        petProfile.appendChild(div1)
    }

    // 반려동물이 없을 때 빈 카드 추가
    if (data.length === 0) {
        const emptyDiv = document.createElement('div')
        emptyDiv.className = "bg-white rounded-xl shadow-lg p-6 text-center hover:shadow-xl transition-all"
        emptyDiv.innerHTML = `
            <div class="w-16 h-16 bg-gradient-to-r from-primary-100 to-secondary-100 rounded-full mx-auto mb-4 flex items-center justify-center">
                <i class="fas fa-plus text-2xl text-primary-600"></i>
            </div>
            <p class="text-gray-500">첫 번째 반려동물을 등록해보세요</p>
        `
        petProfile.appendChild(emptyDiv)
    }
}

// 반려동물 프로필 모달 표시
async function showPetProfile(pet) {
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
    
    // 모달 표시
    viewPetModal.classList.remove('hidden')
    viewPetModal.querySelector('.bg-white').classList.add('modal-enter')
}

// 페르소나 정보 가져오기
async function getPersonaInfo(petId) {
    const response = await fetch(`/api/get-persona/${petId}`)
    const data = await response.json()
    console.log(data)
    console.log(data.pet_persona)
    console.log(data.traits)
    return data
}

// 페르소나 정보 렌더링
function renderPersona(data) {
    console.log('render persona')
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
    } else {
        // 페르소나가 있는 경우
        const persona = data.pet_persona
        const traits = data.traits
        
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

        // console.log('Speech Styles:', speechStyles);
        // console.log('Personality Traits:', personalityTraits);

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
            
            // console.log('클릭된 태그:', span.textContent);
            // console.log('저장된 색상 데이터:', {
            //     bgColor: span.dataset.bgColor,
            //     textColor: span.dataset.textColor,
            //     borderColor: span.dataset.borderColor
            // });
            
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
