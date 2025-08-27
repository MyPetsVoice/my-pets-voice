// 페이지 로드
document.addEventListener('DOMContentLoaded', () => {
    // UI 초기화
    initializeDropDown();
    initializeChat();

    // 첫번째 펫 자동 선택
    if (allPets && allPets.length > 0) {
        selectPet(allPets[0])
    } else {
        showNoPetsMessages();
    }

})

const petDropdownBtn = document.getElementById('pet-dropdown-btn')
const petDropdownMenu = document.getElementById('pet-dropdown-menu')
const dropdownArrow = document.getElementById('dropdown-arrow')
const petInfoSection = document.getElementById('pet-info-section')
const chatMessage = document.getElementById('chat-message')
const chatForm = document.getElementById('chat-form')
const messageInput = document.getElementById('message-input')
const resetChatBtn = document.getElementById('reset-chat-btn')





let socket = null;
let selectedPet = null;
let isConnected = false;

// 웹소켓 연결 및 이벤트 핸들러 등록 함수
function connectSocket() {
    // 소켓 연결되어있으면 끊으라는거?
    if (socket && socket.connected) {
        socket.disconnect();
    }

    console.log('SocketIO 연결 시도...');
    socket = io();

}

function setupEventHandlers() {
    // 연결 성공
    socket.on('connect', () => {
        console.log('SocketIO 연결됨');
        isConnected = true;
        updateConnectionStatus(true);//////
    
        if (selectedPet) {
            socket.emit('select_pet', {
                pet_id: selectedPet.pet_id,
                pet_data: selectedPet
            });
        }
    })

    // 굳이...? 연결 상태 확인...?
    socket.on('connected', function(date) {
        console.log('서버 연결 확인 수신 : ', data.message);
    })

    // 웹소켓 연결 후 선택된 펫 정보 서버로 보낸 후 다시 받은 경우인가?
    socket.on('pet_selected', function(data) {
        if (data.success) {
            console.log('펫 선택 성공: ', data.pet_name);
            showWelcomeMesaage(selectedPet);
            enableChat();
        }
    })

    // 굳이...? 채팅 연결상태....? 위에 꺼랑 뭔 차이? 처음에 연결됐느냐와 채팅 연결이 됐느냐..?
    socket.on('chat_status', function(data) {
        console.log('채팅 상태: ', data);
        if (data.pet_selected) {
            updateChatStatus($)
        }
    })
    

    // send message
    socket.on('send_message', () => {
        addMessage(data.message, 'user')

    })
    
    socket.on('bot_typing', function(data) {
        showTypingIndicator(data.pet_name)
    })

    socket.on('bot_response', function(data) {
        hideTypingIndicator();
        addMessage(data.message, 'bot, data.pet_name');
    })

    socket.on('error', function(data) {
        hideTypingIndicator();
        addMessage(data.message, 'error');
    })

    // reset chat
    socket.on('reset_message', function(data) {
        clearChatMessage();
        if (selectedPet) {
            showWelcomeMesaage(seletedPet);
        }
    })
    
    // disconnect
    socket.on('disconnect', () => {
        isConnected = false;
        updateConnectionStatus(false);
    })


}
function updateConnectionStatus(connected) {
    const headerStatus = document.getElementById('chat-header-status');
    if (connected) {
        headerStatus.textContent = '온라인'
    } else {
        headerStatus.textContent = '연결 중'
    }
}

function sendMessage() {
    const message = messageInput.value.trim()

    if (!message) return;
    if (!selectedPet) {
        alert('반려동물 먼저 선택하세요')
        return;
    }
    if (!socket || !isConnected) {
        alert('서버와 연결이 끊어짐. 페이지 새로고침')
        return;
    }

    // 입력창 클리어
    messageInput.value = '';
    
    // 서버로 메시지 전송
    socket.emit('send_message', {
        message: message,
        pet_id: selectedPet.pet_id
    });
};

function addMessage(text, type, petName = null) {
    const messageDiv = document.createElement('div');
    const timestamp = new Date().toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})

    if (type === 'user') {
        messageDiv.innerHTML = '사용자 메시지 박스 렌더링'
    } else if (type ===' bot'){
        messageDiv.innerHTML = '봇 메시지 박스 렌더링'
    }

}

function showTypingIndicator(petName) {
    hideTypingIndicator(); // 기존 인디케이터 제거

}


function initializeDropDown() {

}

function initializeChat() {

}

function selectPet(petData) {
    selectedPet = petData;

    // UI 업데이트
    updatePetInfoSection(petData);
    updateChatHeader(petData);

    // 웹소켓 연결 시작
    connectSocket();
}

function showNoPetsMessages() {

}

