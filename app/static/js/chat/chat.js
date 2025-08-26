// 페이지 로드
document.addEventListener('DOMContentLoaded', () => {
    // UI 초기화
    initializeDropDown();
    initializeChat();

    console.log(allPets)
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
const chatHeaderTitle = document.getElementById('chat-header-title')
const chatHeaderStatus = document.getElementById('chat-header-status')
const chatMessages = document.getElementById('chat-messages')
const chatForm = document.getElementById('chat-form')
const messageInput = document.getEleyId('message-input')


petDropdownBtn.addEventListener('click', () => {
    petDropdownMenu.classList.remove('hidden')
})







let socket = null;
// let selectedPet = null; chat.html에서 선언되어있음.
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
// 이벤트 핸들러 등록
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

    socket.on('disconnect', () => {
        console.log('SocketIO 연결 해제');
        isConnected = false;
        updateConnectionStatus(false);
    })


    // send message
    socket.on('send_message', () => {
        // 사용자 메시지 전송
        // 사용자 메시지 렌더링
        // 봇 타이핑 렌더링
        // 봇 응답 렌더링
    })




    // reset chat
    socket.on('reset_chat', () => {

    })



}
function updateConnectionStatus() {

}

// 펫 선택 드롭다운 메뉴 이벤트 리스너 등록 - 이벤트 위임
function initializeDropDown() {
    petDropdownMenu.addEventListener('click', (e) => {
        if (e.target.tagName === 'BUTTON') {
            const petData = e.target.dataset.pet 
            console.log(petData)
            selectPet(petData)

            petDropdownMenu.classList.add('hidden')
        }
    })
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

function updatePetInfoSection(petData) {
    console.log('pet 정보로 렌더링')


}

function updateChatHeader(petData) {
    console.log('pet 이름 채팅창에 표시')
}

function showNoPetsMessages() {

}

