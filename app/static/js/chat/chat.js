// 페이지 로드
document.addEventListener('DOMContentLoaded', () => {
    // UI 초기화
    initializeDropDown();
    initializeChat();
    initializePetInfoToggle();

    console.log('전체 펫 목록:', allPets)
    
    // 첫번째 펫 자동 선택
    if (allPets && allPets.length > 0) {
        selectPet(allPets[0])
    } else {
        showNoPetsMessages();
    }
})

const petDropdownBtn = document.getElementById('pet-dropdown-btn')
const dropdownArrow = document.getElementById('dropdown-arrow')
const petDropdownMenu = document.getElementById('pet-dropdown-menu')
const petInfoSection = document.getElementById('pet-info-section')
const resetChatBtn = document.getElementById('reset-chat-btn')
const chatMessages = document.getElementById('chat-messages')
const chatForm = document.getElementById('chat-form')
const messageInput = document.getElementById('message-input')


let socket = null;
// let selectedPet = null; chat.html에서 선언되어있음.
let isConnected = false;


// 펫 선택 드롭다운 메뉴 토글
petDropdownBtn.addEventListener('click', () => {
    petDropdownMenu.classList.toggle('hidden')
})

// 외부 클릭 시 드롭다운 닫기
document.addEventListener('click', (e) => {
    if (!petDropdownBtn.contains(e.target) && !petDropdownMenu.contains(e.target)){
        petDropdownMenu.classList.add('hidden')
    }
})

// 웹소켓 연결 및 이벤트 핸들러 등록 함수
async function connectSocket() {
    // 기존 소켓 연결 해제
    if (socket && socket.connected) {
        console.log('기존 SocketIO 연결 해제')
        socket.disconnect();
        socket = null;
        
        // 연결 해제가 완료될 때까지 잠시 대기
        await new Promise(resolve => setTimeout(resolve, 200));
    }

    console.log('SocketIO 연결 시도...');
    socket = io();
    setupEventHandlers();
}

// 이벤트 핸들러 등록
function setupEventHandlers() {
    // 연결 성공
    socket.on('connect', () => {
        console.log('SocketIO 연결됨');
        isConnected = true;
        updateConnectionStatus(true);

        if (selectedPet) {
            console.log('채팅할 펫 정보 : ', selectedPet)
            socket.emit('join_chat', selectedPet) // 이 때 tts 정보도 같이 보냄?
        }
    })

    socket.on('disconnect', () => {
        console.log('SocketIO 연결 해제');
        isConnected = false;
        updateConnectionStatus(false);
    })

    socket.on('chat_ready', (data) => {
        console.log('채팅 준비 완료 : ', data.message)
        console.log('채팅 할 펫 : ', data.pet_name)

        updateChatHeader(data.pet_name)
    })
    
    // send message
    socket.on('user_message', (data) => {
        // 사용자 메시지 전송
        console.log('서버로부터 받은 사용자 메시지 : ', data.message)
        // 사용자 메시지 렌더링
        addMessage('user', data.message)
    })
    
    socket.on('bot_typing', (data) => {        
        // 봇 타이핑 렌더링
        console.log('봇 타이핑 인디케이터 : ', data.pet_name)
        // 봇 응답 렌더링
        showTypingIndicator(data.pet_name)
    })
    
    socket.on('bot_response', (data) => {
        console.log('펫의 응답 : ', data.message)
        requestTTS(data.message) // tts 요청
        hideTypingIndicator()
        addMessage('bot', data.message, data.pet_name)
    })
    
    // reset chat
    socket.on('reset_chat', () => {
        console.log('채팅 내용 리셋')
        resetChat()
    })
}


function updateConnectionStatus(status) {
    const statusText = document.getElementById('status-text')
    const chatStatusIcon = document.getElementById('chat-status-icon')
    if (status) {
        statusText.textContent = '온라인'
        chatStatusIcon.classList.add('text-green-500')
    } else {
        statusText.textContent = '대기중'
        chatStatusIcon.classList.remove('text-green-500')

    }
}

// 펫 선택 드롭다운 메뉴 이벤트 리스너 등록 - 이벤트 위임
function initializeDropDown() {
    petDropdownMenu.addEventListener('click', (e) => {
        if (e.target.tagName === 'BUTTON') {
            const petData = JSON.parse(e.target.dataset.pet);
            console.log(petData)
            selectPet(petData)
            petDropdownMenu.classList.add('hidden')
        }
    })
}

// 채팅 창 관련 이벤트 위임
function initializeChat() {
    // 폼 제출 이벤트
    chatForm.addEventListener('submit', function(e) {
        e.preventDefault();
        sendMessage();
    });
    
    // Enter 키 처리
    messageInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    });
    
    // 채팅 초기화 버튼
    if (resetChatBtn) {
        resetChatBtn.addEventListener('click', function() {
            if (confirm('정말로 대화를 초기화하시겠습니까?')) {
                resetChat();
            }
        });
    }    
}

// 펫 선택 - 페르소나 정보 가져와야함
async function selectPet(petData) {
    selectedPet = petData;
    petId = petData.pet_id
    const petDropdownBtnText = document.getElementById('pet-dropdown-btn-text')
    petDropdownBtnText.innerText = `${selectedPet.pet_name}(${selectedPet.species_name})`
    
    const response = await fetch(`/api/get_persona/${petId}`)
    const data = await response.json()
    console.log(data)
    const personaInfo = data.persona_info
    
    console.log('selectPet에서 입력된 petData', petData)
    
    // UI 업데이트
    updatePetInfoSection(petData, personaInfo);
    
    // 웹소켓 연결 시작
    await connectSocket();
    
    enableChat()
}

function updatePetInfoSection(petData , personaInfo) {
    petInfoSection.classList.remove('hidden')
    
    // 기본 정보 업데이트
    // document.getElementById('pet-name').textContent = petData.pet_name
    // document.getElementById('pet-species').textContent = petData.species_name
    document.getElementById('pet-age').textContent = `${petData.pet_age}살`
    document.getElementById('pet-gender').textContent = petData.pet_gender
    document.getElementById('pet-breed').textContent = petData.breed_name || '믹스'
    
    // 페르소나 정보 업데이트
    document.getElementById('pet-user-call').textContent = personaInfo.user_call || '-'

    // 성격 특성을 예쁜 태그로 표시
    const personalityContainer = document.getElementById('pet-personality')
    if (personaInfo.traits && personaInfo.traits.length > 0) {
        personalityContainer.innerHTML = personaInfo.traits.map((trait) => {
            return `
                <span class="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-red-100 text-red-800 shadow-sm">
                    ${trait.trait_name}
                </span>
            `
        }).join('')
    } else {
        personalityContainer.innerHTML = `
            <span class="text-gray-500 text-xs italic">설정된 성격 특성이 없습니다</span>
        `
    }

    // 말투를 두 개의 div로 분리 표시
    const politenessElement = document.getElementById('pet-politeness')
    const speechStyleElement = document.getElementById('pet-speech-style')
    
    // 존댓말/반말 표시
    if (personaInfo.politeness) {
        const politenessText = personaInfo.politeness.toLowerCase() === 'formal' ? '존댓말' : '반말'
        politenessElement.textContent = politenessText
    } else {
        politenessElement.textContent = '-'
    }
    
    // 스타일명 표시
    if (personaInfo.style_name) {
        speechStyleElement.textContent = personaInfo.style_name
    } else {
        speechStyleElement.textContent = '-'
    }
    
    // 좋아하는 것 표시
    const likesSection = document.getElementById('pet-likes-section')
    const likesContainer = document.getElementById('pet-likes')
    if (personaInfo.likes && personaInfo.likes.trim()) {
        const likesArray = personaInfo.likes.split(',').map(item => item.trim()).filter(item => item)
        if (likesArray.length > 0) {
            likesSection.classList.remove('hidden')
            likesContainer.innerHTML = likesArray.map(like => `
                <span class="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800">
                    <i class="fas fa-heart text-xs mr-1"></i>
                    ${like}
                </span>
            `).join('')
        } else {
            likesSection.classList.add('hidden')
        }
    } else {
        likesSection.classList.add('hidden')
    }
    
    // 싫어하는 것 표시
    const dislikesSection = document.getElementById('pet-dislikes-section')
    const dislikesContainer = document.getElementById('pet-dislikes')
    if (personaInfo.dislikes && personaInfo.dislikes.trim()) {
        const dislikesArray = personaInfo.dislikes.split(',').map(item => item.trim()).filter(item => item)
        if (dislikesArray.length > 0) {
            dislikesSection.classList.remove('hidden')
            dislikesContainer.innerHTML = dislikesArray.map(dislike => `
                <span class="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-red-100 text-red-800">
                    <i class="fas fa-times text-xs mr-1"></i>
                    ${dislike}
                </span>
            `).join('')
        } else {
            dislikesSection.classList.add('hidden')
        }
    } else {
        dislikesSection.classList.add('hidden')
    }

}

function updateChatHeader(petName) {
    console.log('updateChatHeader 입력 변수 : ', petName)
    const chatHeaderTitle = document.getElementById('chat-header-title')
    
    chatHeaderTitle.textContent = `${petName}(이)와의 대화`

    showWelcomeMessage(petName)


}


function enableChat() {
    const msgSubmitBtn = document.getElementById('msg-submit-btn')
    
    messageInput.placeholder = `${selectedPet.pet_name}(이)에게 메시지를 보내 대화를 시작하세요.`
    messageInput.disabled = false;
    
    msgSubmitBtn.disabled = false;
    msgSubmitBtn.className = 'px-6 py-3 bg-gradient-to-r from-primary-500 to-secondary-500 text-white rounded-lg hover:from-primary-600 hover:to-secondary-600 transition-all';
    
    messageInput.focus();
}

function sendMessage() {
    const userMsg = messageInput.value;
    socket.emit('send_message', {'message': userMsg})
    messageInput.value = ''
}

function addMessage(type, content, senderName = null) {
    deleteWelcomeMessage()
    
    const messageDiv = document.createElement('div');
    messageDiv.className = `flex ${type === 'user' ? 'justify-end' : 'justify-start'} mb-4`;
    
    const messageContent = document.createElement('div');
    messageContent.className = `max-w-xs lg:max-w-md px-4 py-2 rounded-lg ${
        type === 'user' 
            ? 'bg-primary-500 text-white' 
            : 'bg-white border border-gray-200 text-gray-800 shadow-sm'
    }`;
    
    if (type === 'bot' && senderName) {
        const nameSpan = document.createElement('div');
        nameSpan.className = 'text-xs text-gray-500 mb-1';
        nameSpan.textContent = senderName;
        messageContent.appendChild(nameSpan);
    }
    
    const textDiv = document.createElement('div');
    textDiv.textContent = content;
    messageContent.appendChild(textDiv);
    
    messageDiv.appendChild(messageContent);
    chatMessages.appendChild(messageDiv);
    
    // 스크롤을 맨 아래로 부드럽게
    scrollToBottom();
}

// 타이핑 인디케이터 표시
function showTypingIndicator(petName) {
    hideTypingIndicator();
    
    const typingDiv = document.createElement('div');
    typingDiv.id = 'typing-indicator';
    typingDiv.className = 'flex justify-start mb-4';
    
    const typingContent = document.createElement('div');
    typingContent.className = 'max-w-xs lg:max-w-md px-4 py-2 rounded-lg bg-gray-100 border border-gray-200';
    
    const nameSpan = document.createElement('div');
    nameSpan.className = 'text-xs text-gray-500 mb-1';
    nameSpan.textContent = petName;
    typingContent.appendChild(nameSpan);
    
    const dotsDiv = document.createElement('div');
    dotsDiv.className = 'flex space-x-1';
    dotsDiv.innerHTML = `
        <div class="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style="animation-delay: 0ms;"></div>
        <div class="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style="animation-delay: 150ms;"></div>
        <div class="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style="animation-delay: 300ms;"></div>
    `;
    typingContent.appendChild(dotsDiv);
    
    typingDiv.appendChild(typingContent);
    chatMessages.appendChild(typingDiv);
    
    scrollToBottom();
}

// 타이핑 인디케이터 숨기기
function hideTypingIndicator() {
    const typingIndicator = document.getElementById('typing-indicator');
    if (typingIndicator) {
        typingIndicator.remove();
    }
}

// 채팅 메시지 스크롤 함수
function scrollToBottom() {
    if (chatMessages) {
        chatMessages.scrollTo({
            top: chatMessages.scrollHeight,
            behavior: 'smooth'
        });
    }
}

function resetChat() {
    chatMessages.innerHTML = '';
    // 기존에 있던 거 추가하기
    showWelcomeMessage(selectedPet.pet_name)
}

function showNoPetsMessages() {
    const div = document.createElement('div')
    div.innerHTML = `
        <div class="text-center py-12">
            <div class="bg-white rounded-xl shadow-lg p-8 max-w-md mx-auto">
                <i class="fas fa-robot text-6xl text-gray-400 mb-4"></i>
                <h2 class="text-xl font-bold text-gray-800 mb-2">페르소나를 먼저 생성하세요</h2>
                <p class="text-gray-600 mb-6">반려동물과 대화하려면 먼저 마이페이지에서 페르소나를 생성해야 합니다.</p>
                <a href="{{ url_for('mypage.mypage_views.mypage') }}" 
                   class="inline-flex items-center px-6 py-3 bg-gradient-to-r from-primary-500 to-secondary-500 text-white rounded-lg hover:from-primary-600 hover:to-secondary-600 transition-all">
                    <i class="fas fa-user-plus mr-2"></i>
                    마이페이지로 가기
                </a>
            </div>
        </div>`
}

function showSelectPetMessage() {
    chatMessages.innerHTML = `
        <div id="welcome-on-boarding" class="text-center py-12">
            <i class="fas fa-comments text-6xl text-gray-300 mb-4"></i>
            <h3 id="chat-with-pet" class="text-xl font-bold text-gray-600 mb-2">반려동물과 대화하기</h3>
            <p class="text-gray-500">왼쪽에서 반려동물을 선택하고 대화를 시작해보세요!</p>
        </div>
    `
}

function showWelcomeMessage(petName) {
    chatMessages.innerHTML = `
        <div id="welcome-msg" class="text-center py-8">
            <i class="fas fa-heart text-4xl text-primary-400 mb-4"></i>
            <p class="text-gray-600"><span id="welcome-pet">${petName}(이)와 대화를 시작해보세요!</span></p>
        </div>
    `
}
function deleteWelcomeMessage() {
    const welcomeMsg = document.getElementById('welcome-msg')
    if (welcomeMsg) {
        chatMessages.innerHTML = ``
    }
}

// 반려동물 정보 토글 기능 초기화
function initializePetInfoToggle() {
    const toggleBtn = document.getElementById('pet-info-toggle');
    const arrow = document.getElementById('pet-info-arrow');
    const content = document.getElementById('pet-info-content');
    
    if (toggleBtn && arrow && content) {
        toggleBtn.addEventListener('click', function() {
            // 드롭다운 토글
            content.classList.toggle('show');
            arrow.classList.toggle('rotate-180');
        });
    }
}

    