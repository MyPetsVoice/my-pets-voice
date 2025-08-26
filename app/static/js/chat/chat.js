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
    // reset chat
    // disconnect



}
function updateConnectionStatus() {

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

