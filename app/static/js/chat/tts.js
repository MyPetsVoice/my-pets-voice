// TTS 목소리 옵션
const voiceOptions = [
    { id: 'alloy', name: 'Alloy', gender: 'neutral' },
    { id: 'ash', name: 'Ash', gender: 'male' },
    { id: 'ballad', name: 'Ballad', gender: 'female' },
    { id: 'coral', name: 'Coral', gender: 'female' },
    { id: 'echo', name: 'Echo', gender: 'male' },
    { id: 'fable', name: 'Fable', gender: 'british' },
    { id: 'nova', name: 'Nova', gender: 'female' },
    { id: 'onyx', name: 'Onyx', gender: 'male' },
    { id: 'sage', name: 'Sage', gender: 'neutral' },
    { id: 'shimmer', name: 'Shimmer', gender: 'female' }
];

// TTS 설정 관리 객체
const TTSSettings = {
    getSelectedVoice() {
        return localStorage.getItem('tts-voice') || 'alloy';
    },
    
    setSelectedVoice(voiceId) {
        localStorage.setItem('tts-voice', voiceId);
    },
    
    isEnabled() {
        return localStorage.getItem('tts-enabled') !== 'false';
    },
    
    setEnabled(enabled) {
        localStorage.setItem('tts-enabled', enabled.toString());
    },
    
    toggle() {
        const currentState = this.isEnabled();
        this.setEnabled(!currentState);
        return !currentState;
    }
};

// DOM 로딩 완료 후 실행
document.addEventListener('DOMContentLoaded', function() {
    const ttsSettingsBtn = document.getElementById('tts-settings-btn');
    const headerToggle = document.getElementById('tts-enable-toggle-header');
    
    if (ttsSettingsBtn) {
        ttsSettingsBtn.addEventListener('click', openTTSModal);
        createTTSModal();
        loadTTSSettings();
    }
    
    // 헤더 토글 이벤트 리스너
    if (headerToggle) {
        headerToggle.addEventListener('change', function() {
            TTSSettings.setEnabled(this.checked);
            updateTTSButton();
            updateVoiceOptionsState(); // 모달이 열려있을 때 목소리 선택 영역도 업데이트
            console.log('TTS 상태 변경:', this.checked ? '활성화' : '비활성화');
        });
        
        // 초기 상태 설정
        headerToggle.checked = TTSSettings.isEnabled();
    }

    console.log('local Stroage : ', localStorage)
});

// TTS 모달 생성
function createTTSModal() {
    const modalHTML = `
        <div id="tts-modal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 hidden">
            <div class="bg-white rounded-lg shadow-xl max-w-md w-full mx-4">
                <div class="p-6">
                    <div class="flex justify-between items-center mb-4">
                        <h3 class="text-lg font-semibold text-gray-800">
                            <i class="fas fa-volume-up text-primary-500 mr-2"></i>
                            TTS 음성 설정
                        </h3>
                        <button id="close-tts-modal" class="text-gray-400 hover:text-gray-600 transition-colors">
                            <i class="fas fa-times text-xl"></i>
                        </button>
                    </div>
                    
                    
                    <div class="space-y-3">
                        <h4 class="text-sm font-medium text-gray-700 mb-2">목소리 선택:</h4>
                        <div id="voice-options" class="flex flex-wrap gap-2">
                            ${voiceOptions.map(voice => `
                                <button class="voice-option flex items-center px-3 py-2 border border-gray-200 rounded-full hover:border-primary-300 transition-colors text-sm ${voice.id === TTSSettings.getSelectedVoice() ? 'border-primary-500 bg-primary-50 text-primary-700' : 'text-gray-700'}" 
                                        data-voice="${voice.id}">
                                    <div class="w-5 h-5 bg-gradient-to-r from-primary-100 to-secondary-100 rounded-full mr-2 flex items-center justify-center">
                                        <i class="fas fa-user-circle text-primary-600 text-xs"></i>
                                    </div>
                                    <span class="font-medium">${voice.name}</span>
                                    <span class="text-xs text-gray-500 ml-1">(${voice.gender})</span>
                                    <div class="voice-selected-indicator ml-2 ${voice.id === TTSSettings.getSelectedVoice() ? '' : 'hidden'}">
                                        <i class="fas fa-check text-primary-500 text-xs"></i>
                                    </div>
                                </button>
                            `).join('')}
                        </div>
                    </div>
                    
                    <div class="flex gap-3 mt-6">
                        <button id="cancel-tts-settings" class="flex-1 px-4 py-2 text-gray-600 bg-gray-100 rounded-lg hover:bg-gray-200 transition-colors">
                            취소
                        </button>
                        <button id="save-tts-settings" class="flex-1 px-4 py-2 text-white bg-gradient-to-r from-primary-500 to-secondary-500 rounded-lg hover:from-primary-600 hover:to-secondary-600 transition-all">
                            적용
                        </button>
                    </div>
                </div>
            </div>
        </div>
    `;
    
    document.body.insertAdjacentHTML('beforeend', modalHTML);
    
    // 모달 이벤트 리스너 설정
    setupTTSModalEvents();
}

// TTS 모달 열기
function openTTSModal() {
    const modal = document.getElementById('tts-modal');
    if (modal) {
        modal.classList.remove('hidden');
        document.body.style.overflow = 'hidden';
    }
}

// TTS 모달 닫기
function closeTTSModal() {
    const modal = document.getElementById('tts-modal');
    if (modal) {
        modal.classList.add('hidden');
        document.body.style.overflow = 'auto';
    }
}

// TTS 모달 이벤트 설정
function setupTTSModalEvents() {
    const modal = document.getElementById('tts-modal');
    const closeBtn = document.getElementById('close-tts-modal');
    const cancelBtn = document.getElementById('cancel-tts-settings');
    const saveBtn = document.getElementById('save-tts-settings');
    const voiceOptions = document.querySelectorAll('.voice-option');
    
    // 모달 외부 클릭시 닫기
    modal.addEventListener('click', function(e) {
        if (e.target === modal) {
            closeTTSModal();
        }
    });
    
    // 닫기 버튼
    closeBtn.addEventListener('click', closeTTSModal);
    cancelBtn.addEventListener('click', closeTTSModal);
    
    // 초기 상태 설정 - TTS 비활성화시 목소리 선택 영역 비활성화
    updateVoiceOptionsState();
    
    // 목소리 선택
    voiceOptions.forEach(option => {
        option.addEventListener('click', function() {
            if (TTSSettings.isEnabled()) {
                const voiceId = this.dataset.voice;
                selectVoice(voiceId);
            }
        });
    });
    
    // 저장 버튼
    saveBtn.addEventListener('click', function() {
        saveTTSSettings();
        closeTTSModal();
    });
}

// 목소리 선택 영역 상태 업데이트
function updateVoiceOptionsState() {
    const voiceOptionsContainer = document.getElementById('voice-options').parentElement;
    if (voiceOptionsContainer) {
        if (TTSSettings.isEnabled()) {
            voiceOptionsContainer.classList.remove('opacity-50', 'pointer-events-none');
        } else {
            voiceOptionsContainer.classList.add('opacity-50', 'pointer-events-none');
        }
    }
}

// 목소리 선택
function selectVoice(voiceId) {
    
    // 모든 선택 표시 숨기기
    document.querySelectorAll('.voice-selected-indicator').forEach(indicator => {
        indicator.classList.add('hidden');
    });
    
    // 모든 선택 스타일 제거
    document.querySelectorAll('.voice-option').forEach(option => {
        option.classList.remove('border-primary-500', 'bg-primary-50', 'text-primary-700');
        option.classList.add('border-gray-200', 'text-gray-700');
    });
    
    // 선택된 목소리 강조
    const selectedOption = document.querySelector(`[data-voice="${voiceId}"]`);
    if (selectedOption) {
        selectedOption.classList.add('border-primary-500', 'bg-primary-50', 'text-primary-700');
        selectedOption.classList.remove('border-gray-200', 'text-gray-700');
        selectedOption.querySelector('.voice-selected-indicator').classList.remove('hidden');
    }
}

// TTS 설정 저장
function saveTTSSettings() {
    const currentVoice = getCurrentSelectedVoice();
    
    TTSSettings.setSelectedVoice(currentVoice);
    updateTTSButton();
    console.log('TTS 목소리 설정 저장됨:', currentVoice);
}

// 현재 UI에서 선택된 목소리 가져오기
function getCurrentSelectedVoice() {
    const selectedOption = document.querySelector('.voice-option.border-primary-500');
    return selectedOption ? selectedOption.dataset.voice : TTSSettings.getSelectedVoice();
}

// TTS 버튼 상태 업데이트
function updateTTSButton() {
    const ttsBtn = document.getElementById('tts-settings-btn');
    if (ttsBtn) {
        const isEnabled = TTSSettings.isEnabled();
        
        if (isEnabled) {
            ttsBtn.classList.remove('opacity-50');
            ttsBtn.innerHTML = '<i class="fas fa-volume-up text-primary-500"></i>';
            ttsBtn.title = 'TTS 음성 재생 활성화됨';
        } else {
            ttsBtn.classList.add('opacity-50');
            ttsBtn.innerHTML = '<i class="fas fa-volume-mute text-gray-400"></i>';
            ttsBtn.title = 'TTS 음성 재생 비활성화됨';
        }
    }
}

// 저장된 설정 로드
function loadTTSSettings() {
    const savedVoice = TTSSettings.getSelectedVoice();
    if (savedVoice && voiceOptions.find(v => v.id === savedVoice)) {
        updateTTSButton();
    }

    console.log(savedVoice)
}

// TTS 활성 상태 확인 함수 (외부에서 사용)
function isTTSEnabled() {
    return TTSSettings.isEnabled();
}


// TTS 요청하기
async function requestTTS(botMessage) {
    const enabled = TTSSettings.isEnabled()
    const voice = TTSSettings.getSelectedVoice()
    
    console.log('TTS 요청:', { enabled, voice, text: botMessage });
    
    if (enabled) {
        try {
            console.log('TTS API 호출 중...');
            
            const response = await fetch('/api/chat/tts',{
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({
                    text: botMessage,
                    voice: voice
                })
            })
            
            console.log('TTS 응답 상태:', response.status, response.headers.get('content-type'));
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            // mp3 스트리밍 응답이므로 blob으로 처리
            const audioBlob = await response.blob();
            console.log('오디오 Blob 크기:', audioBlob.size, '타입:', audioBlob.type);
            
            if (audioBlob.size === 0) {
                throw new Error('빈 오디오 파일');
            }
            
            const audioUrl = URL.createObjectURL(audioBlob);
            const audio = new Audio(audioUrl);
            audio.volume = 1.0; // 최대 볼륨
            
            // 오디오 이벤트 리스너 추가
            audio.addEventListener('loadstart', () => console.log('오디오 로딩 시작'));
            audio.addEventListener('canplay', () => console.log('오디오 재생 가능'));
            audio.addEventListener('play', () => console.log('오디오 재생 시작'));
            audio.addEventListener('ended', () => {
                console.log('오디오 재생 완료');
                URL.revokeObjectURL(audioUrl);
            });
            audio.addEventListener('error', (e) => console.error('오디오 재생 오류:', e));
            
            console.log('오디오 재생 시작...');
            await audio.play();
            
        } catch (error) {
            console.error('TTS 재생 실패:', error);
        }
    } else {
        console.log('TTS 비활성화됨');
    }
}