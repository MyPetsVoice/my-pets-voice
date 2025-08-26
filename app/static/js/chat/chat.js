// SocketIO 연결 설정
const socket = io({
    transports: ['polling', 'websocket'],
    upgrade: false,
    timeout: 20000,
    forceNew: true
});
let isConnected = false;
let currentPetInfo = null;

// SocketIO 이벤트 핸들러 설정
socket.on('connect', function() {
    console.log('SocketIO 연결됨');
    isConnected = true;
    updateConnectionStatus(true);
});

socket.on('disconnect', function() {
    console.log('SocketIO 연결 해제됨');
    isConnected = false;
    updateConnectionStatus(false);
});

socket.on('connect_error', function(error) {
    console.error('SocketIO 연결 에러:', error);
    isConnected = false;
    updateConnectionStatus(false);
    showError('서버 연결에 실패했습니다.');
});

socket.on('user_message', function(data) {
    addMessage('user', data.message);
});

socket.on('bot_typing', function(data) {
    showTypingIndicator(data.pet_name);
});

socket.on('bot_response', function(data) {
    hideTypingIndicator();
    addMessage('bot', data.message, data.pet_name);
});

socket.on('chat_reset', function(data) {
    clearMessages();
    showSystemMessage(data.message);
});

socket.on('error', function(data) {
    hideTypingIndicator();
    showError(data.message);
});

// DOM 요소들
const chatMessages = document.getElementById('chat-messages');
const messageInput = document.getElementById('message-input');
const chatForm = document.getElementById('chat-form');
const petDropdownBtn = document.getElementById('pet-dropdown-btn');
const petDropdownMenu = document.getElementById('pet-dropdown-menu');
const dropdownArrow = document.getElementById('dropdown-arrow');
const petInfoSection = document.getElementById('pet-info-section');
const resetChatBtn = document.getElementById('reset-chat-btn');

// 페이지 로드 시 초기화
document.addEventListener('DOMContentLoaded', function() {
    initializePage();
});

function initializePage() {
    // 드롭다운 이벤트 설정
    setupDropdownEvents();
    
    // 폼 이벤트 설정
    setupFormEvents();
    
    // 채팅 초기화 버튼 이벤트
    setupResetButton();
    
    // 초기 연결 시도
    connectSocket();
}

// 드롭다운 이벤트 설정
function setupDropdownEvents() {
    if (petDropdownBtn) {
        petDropdownBtn.addEventListener('click', function(e) {
            e.stopPropagation();
            toggleDropdown();
        });
    }
    
    // 펫 옵션 클릭 이벤트
    const petOptions = document.querySelectorAll('.pet-option');
    petOptions.forEach(option => {
        option.addEventListener('click', function() {
            const petData = JSON.parse(this.dataset.pet);
            selectPet(petData);
            closeDropdown();
        });
    });
    
    // 외부 클릭시 드롭다운 닫기
    document.addEventListener('click', function() {
        closeDropdown();
    });
}

// 폼 이벤트 설정
function setupFormEvents() {
    if (chatForm) {
        chatForm.addEventListener('submit', function(e) {
            e.preventDefault();
            sendMessage();
        });
    }
    
    if (messageInput) {
        messageInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                sendMessage();
            }
        });
    }
}

// 리셋 버튼 이벤트 설정
function setupResetButton() {
    if (resetChatBtn) {
        resetChatBtn.addEventListener('click', function() {
            if (currentPetInfo) {
                socket.emit('reset_chat');
            }
        });
    }
}

// 드롭다운 토글
function toggleDropdown() {
    if (petDropdownMenu && dropdownArrow) {
        const isOpen = !petDropdownMenu.classList.contains('hidden');
        if (isOpen) {
            closeDropdown();
        } else {
            openDropdown();
        }
    }
}

// 드롭다운 열기
function openDropdown() {
    if (petDropdownMenu && dropdownArrow) {
        petDropdownMenu.classList.remove('hidden');
        dropdownArrow.style.transform = 'rotate(180deg)';
    }
}

// 드롭다운 닫기
function closeDropdown() {
    if (petDropdownMenu && dropdownArrow) {
        petDropdownMenu.classList.add('hidden');
        dropdownArrow.style.transform = 'rotate(0deg)';
    }
}

// 펫 선택
function selectPet(petData) {
    console.log('펫 선택:', petData);
    
    // 드롭다운 버튼 업데이트
    updateDropdownButton(petData);
    
    // 펫 정보를 서버에 설정
    fetch(`/api/set_pet_info/${petData.pet_id}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            console.log('펫 정보 설정 완료:', data.pet_info);
            currentPetInfo = data.pet_info;
            
            // 사이드바 정보 표시
            displayPetInfo(data.pet_info);
            
            // 채팅 헤더 업데이트
            updateChatHeader(data.pet_info);
            
            // 입력창 활성화
            enableChatInput(data.pet_info.name);
            
            // 채팅 메시지 초기화
            clearMessages();
            showWelcomeMessage(data.pet_info.name);
            
            // 소켓 재연결 (펫 정보가 세션에 설정된 후)
            if (socket.connected) {
                socket.disconnect();
                setTimeout(() => {
                    socket.connect();
                }, 100);
            } else {
                socket.connect();
            }
        } else {
            console.error('펫 정보 설정 실패:', data.error);
            showError(`펫 정보를 불러오는데 실패했습니다: ${data.error}`);
        }
    })
    .catch(error => {
        console.error('펫 정보 설정 중 오류:', error);
        showError('펫 정보 설정 중 오류가 발생했습니다.');
    });
}

// 드롭다운 버튼 업데이트
function updateDropdownButton(petData) {
    const selectedPetInfo = document.getElementById('selected-pet-info');
    if (selectedPetInfo) {
        selectedPetInfo.innerHTML = `
            <div class="w-8 h-8 bg-gradient-to-r from-primary-100 to-secondary-100 rounded-full mr-3 flex items-center justify-center">
                ${petData.profile_image_url ? 
                    `<img src="${petData.profile_image_url}" alt="${petData.pet_name}" class="w-full h-full rounded-full object-cover">` :
                    `<i class="fas fa-paw text-primary-600 text-sm"></i>`
                }
            </div>
            <span class="font-medium text-gray-700">${petData.pet_name}</span>
        `;
    }
}

// 펫 정보 표시
function displayPetInfo(petInfo) {
    // 펫 정보 섹션 표시
    if (petInfoSection) {
        petInfoSection.classList.remove('hidden');
    }
    
    // 기본 정보 업데이트
    updateElement('pet-name', petInfo.name);
    updateElement('pet-species', petInfo.species);
    updateElement('pet-age', `${petInfo.age}살`);
    updateElement('pet-gender', petInfo.gender);
    updateElement('pet-breed', petInfo.breed);
    updateElement('pet-speech-style', petInfo.speech_style);
    
    // 아바타 업데이트
    const petAvatar = document.getElementById('pet-avatar');
    if (petAvatar) {
        petAvatar.innerHTML = `<i class="fas fa-paw text-2xl text-primary-600"></i>`;
    }
    
    // 성격 태그 표시
    const personalityContainer = document.getElementById('pet-personality');
    if (personalityContainer && petInfo.personality && petInfo.personality.length > 0) {
        personalityContainer.innerHTML = petInfo.personality.map(trait => 
            `<span class="px-2 py-1 bg-red-100 text-red-800 text-xs rounded-full">${trait}</span>`
        ).join('');
    } else if (personalityContainer) {
        personalityContainer.innerHTML = '<span class="text-gray-500 text-xs">설정된 성격이 없습니다</span>';
    }
    
    // 좋아하는 것 표시
    const likesSection = document.getElementById('pet-likes-section');
    const likesContainer = document.getElementById('pet-likes');
    if (petInfo.likes && petInfo.likes.length > 0) {
        likesSection?.classList.remove('hidden');
        if (likesContainer) {
            likesContainer.textContent = petInfo.likes.join(', ');
        }
    } else {
        likesSection?.classList.add('hidden');
    }
    
    // 싫어하는 것 표시
    const dislikesSection = document.getElementById('pet-dislikes-section');
    const dislikesContainer = document.getElementById('pet-dislikes');
    if (petInfo.dislikes && petInfo.dislikes.length > 0) {
        dislikesSection?.classList.remove('hidden');
        if (dislikesContainer) {
            dislikesContainer.textContent = petInfo.dislikes.join(', ');
        }
    } else {
        dislikesSection?.classList.add('hidden');
    }
}

// 채팅 헤더 업데이트
function updateChatHeader(petInfo) {
    updateElement('chat-header-title', `${petInfo.name}와의 대화`);
    
    const chatHeaderStatus = document.getElementById('chat-header-status');
    if (chatHeaderStatus) {
        chatHeaderStatus.innerHTML = `
            <i class="fas fa-circle text-xs mr-1 ${isConnected ? 'text-green-500' : 'text-gray-400'}"></i>
            ${isConnected ? '온라인' : '연결 중...'}
        `;
    }
}

// 채팅 입력창 활성화
function enableChatInput(petName) {
    if (messageInput) {
        messageInput.disabled = false;
        messageInput.placeholder = `${petName}에게 메시지를 입력하세요...`;
    }
    
    const submitBtn = chatForm?.querySelector('button[type="submit"]');
    if (submitBtn) {
        submitBtn.disabled = false;
        submitBtn.className = 'px-6 py-3 bg-gradient-to-r from-primary-500 to-secondary-500 text-white rounded-lg hover:from-primary-600 hover:to-secondary-600 transition-all';
    }
}

// 연결 상태 업데이트
function updateConnectionStatus(connected) {
    const chatHeaderStatus = document.getElementById('chat-header-status');
    if (chatHeaderStatus && currentPetInfo) {
        chatHeaderStatus.innerHTML = `
            <i class="fas fa-circle text-xs mr-1 ${connected ? 'text-green-500' : 'text-gray-400'}"></i>
            ${connected ? '온라인' : '연결 중...'}
        `;
    }
}

// SocketIO 연결
function connectSocket() {
    console.log('SocketIO 연결 시도 중...');
    
    if (socket.disconnected) {
        socket.connect();
    }
}

// 메시지 전송
function sendMessage() {
    const message = messageInput.value.trim();
    if (!message) return;
    
    if (!isConnected || socket.disconnected) {
        showError('서버와 연결되지 않았습니다. 잠시 후 다시 시도해주세요.');
        return;
    }
    
    if (!currentPetInfo) {
        showError('반려동물을 먼저 선택해주세요.');
        return;
    }
    
    // 메시지 전송
    socket.emit('send_message', {
        message: message
    });
    
    // 입력창 초기화
    messageInput.value = '';
    messageInput.focus();
}

// 메시지 추가
function addMessage(type, content, senderName = null) {
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
    
    // 스크롤을 맨 아래로
    chatMessages.scrollTop = chatMessages.scrollHeight;
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
    
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

// 타이핑 인디케이터 숨기기
function hideTypingIndicator() {
    const typingIndicator = document.getElementById('typing-indicator');
    if (typingIndicator) {
        typingIndicator.remove();
    }
}

// 모든 메시지 제거
function clearMessages() {
    chatMessages.innerHTML = '';
}

// 환영 메시지 표시
function showWelcomeMessage(petName) {
    const welcomeDiv = document.createElement('div');
    welcomeDiv.className = 'text-center py-8';
    welcomeDiv.innerHTML = `
        <i class="fas fa-heart text-4xl text-primary-400 mb-4"></i>
        <p class="text-gray-600">${petName}와 대화를 시작해보세요!</p>
    `;
    chatMessages.appendChild(welcomeDiv);
}

// 시스템 메시지 표시
function showSystemMessage(message) {
    const systemDiv = document.createElement('div');
    systemDiv.className = 'text-center py-4';
    
    const messageSpan = document.createElement('span');
    messageSpan.className = 'inline-block px-4 py-2 bg-blue-100 text-blue-800 text-sm rounded-lg';
    messageSpan.textContent = message;
    
    systemDiv.appendChild(messageSpan);
    chatMessages.appendChild(systemDiv);
    
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

// 에러 메시지 표시
function showError(message) {
    const errorDiv = document.createElement('div');
    errorDiv.className = 'text-center py-4';
    
    const errorSpan = document.createElement('span');
    errorSpan.className = 'inline-block px-4 py-2 bg-red-100 text-red-800 text-sm rounded-lg';
    errorSpan.textContent = message;
    
    errorDiv.appendChild(errorSpan);
    chatMessages.appendChild(errorDiv);
    
    chatMessages.scrollTop = chatMessages.scrollHeight;
    
    // 3초 후 에러 메시지 제거
    setTimeout(() => {
        errorDiv.remove();
    }, 3000);
}

// 헬퍼 함수: 요소 내용 업데이트
function updateElement(id, content) {
    const element = document.getElementById(id);
    if (element) {
        element.textContent = content || '-';
    }
}