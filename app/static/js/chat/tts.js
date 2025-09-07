class PetTTSManager {
    constructor() {
        this.currentPetId = null;
        this.currentSettings = {};
        this.isPlaying = false;
        this.availableVoices = {};
        
        this.setupUI();
        this.loadAvailableVoices();
    }
    
    // 현재 선택된 반려동물 설정
    setCurrentPet(petId) {
        console.log('set current pet : ', petId)
        this.currentPetId = petId;
        this.loadPetSettings(petId);
    }
    
    async loadPetSettings(petId) {
        try {
            const response = await fetch(`/api/tts/pet-settings/${petId}`);
            const data = await response.json();
            
            if (data.success) {
                this.currentSettings = data.settings;
                this.updateTTSButton();
                this.updateModalContent();
            } else {
                console.error('TTS 설정 로드 실패:', data.error);
            }
        } catch (error) {
            console.error('TTS 설정 로드 실패:', error);
        }
    }
    
    setupUI() {
        this.createTTSButton();
        this.createTTSModal();
    }
    
    createTTSButton() {
        // 이미 헤더에 버튼이 있으므로 이벤트만 바인딩
        const ttsButton = document.getElementById('tts-settings-btn');
        if (ttsButton) {
            ttsButton.addEventListener('click', () => {
                if (this.currentPetId) {
                    this.showTTSModal();
                } else {
                    this.showToast('먼저 반려동물을 선택해주세요.', 'warning');
                }
            });
        }
    }
    
    createTTSModal() {
        const modalHTML = `
            <div id="pet-tts-modal" class="fixed inset-0 bg-black bg-opacity-50 hidden items-center justify-center z-50 p-4">
                <div class="bg-white rounded-lg p-6 max-w-md w-full max-h-[90vh] overflow-y-auto">
                    <div class="flex justify-between items-center mb-4">
                        <div>
                            <h3 class="text-lg font-semibold">TTS 음성 설정</h3>
                            <p id="modal-pet-name" class="text-sm text-gray-600"></p>
                        </div>
                        <button id="close-pet-tts-modal" class="text-gray-500 hover:text-gray-700">
                            <i class="fas fa-times"></i>
                        </button>
                    </div>
                    
                    <div class="space-y-4">
                        <!-- TTS 활성화/비활성화 -->
                        <div class="flex items-center justify-between">
                            <label class="text-sm font-medium text-gray-700">음성 출력</label>
                            <label class="relative inline-flex items-center cursor-pointer">
                                <input type="checkbox" id="pet-tts-enabled" class="sr-only peer">
                                <div class="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
                            </label>
                        </div>
                        
                        <!-- TTS 제공업체 선택 -->
                        <div>
                            <label class="block text-sm font-medium text-gray-700 mb-2">TTS 제공업체</label>
                            <select id="pet-tts-provider" class="w-full p-2 border border-gray-300 rounded-lg focus:border-blue-500 focus:ring-2 focus:ring-blue-200">
                                <option value="openai">OpenAI TTS</option>
                                <option value="gemini">Gemini TTS</option>
                            </select>
                        </div>
                        
                        <!-- 음성 선택 -->
                        <div>
                            <label class="block text-sm font-medium text-gray-700 mb-2">음성 선택</label>
                            <div id="voice-categories" class="space-y-2">
                                <!-- 음성 카테고리들이 동적으로 추가됨 -->
                            </div>
                        </div>
                        
                        <!-- 속도 설정 -->
                        <div>
                            <label class="block text-sm font-medium text-gray-700 mb-2">
                                속도: <span id="pet-speed-value">0</span>
                            </label>
                            <input type="range" id="pet-speed-range" min="-5" max="5" step="1" value="0" 
                                   class="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer">
                            <div class="flex justify-between text-xs text-gray-500 mt-1">
                                <span>느림</span>
                                <span>보통</span>
                                <span>빠름</span>
                            </div>
                        </div>
                        
                        <!-- 높낮이 설정 -->
                        <div>
                            <label class="block text-sm font-medium text-gray-700 mb-2">
                                높낮이: <span id="pet-pitch-value">0</span>
                            </label>
                            <input type="range" id="pet-pitch-range" min="-5" max="5" step="1" value="0" 
                                   class="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer">
                            <div class="flex justify-between text-xs text-gray-500 mt-1">
                                <span>낮음</span>
                                <span>보통</span>
                                <span>높음</span>
                            </div>
                        </div>
                        
                        <!-- 감정 설정 -->
                        <div>
                            <label class="block text-sm font-medium text-gray-700 mb-2">감정</label>
                            <select id="pet-emotion-select" class="w-full p-2 border border-gray-300 rounded-lg focus:border-blue-500 focus:ring-2 focus:ring-blue-200">
                                <option value="0">보통</option>
                                <option value="1">슬픔</option>
                                <option value="2">기쁨</option>
                                <option value="3">분노</option>
                            </select>
                        </div>
                        
                        <!-- 볼륨 설정 -->
                        <div>
                            <label class="block text-sm font-medium text-gray-700 mb-2">
                                볼륨: <span id="pet-volume-value">0</span>
                            </label>
                            <input type="range" id="pet-volume-range" min="-5" max="5" step="1" value="0" 
                                   class="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer">
                        </div>
                        
                        <!-- 버튼들 -->
                        <div class="flex gap-2">
                            <button id="test-pet-tts" class="flex-1 bg-blue-500 text-white py-2 px-4 rounded-lg hover:bg-blue-600 transition-colors">
                                <i class="fas fa-play mr-2"></i>테스트
                            </button>
                            <button id="save-pet-tts-settings" class="flex-1 bg-green-500 text-white py-2 px-4 rounded-lg hover:bg-green-600 transition-colors">
                                <i class="fas fa-save mr-2"></i>저장
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        document.body.insertAdjacentHTML('beforeend', modalHTML);
        this.bindModalEvents();
    }
    
    bindModalEvents() {
        // 모달 닫기
        document.getElementById('close-pet-tts-modal').addEventListener('click', () => {
            this.hideTTSModal();
        });
        
        // 배경 클릭시 모달 닫기
        document.getElementById('pet-tts-modal').addEventListener('click', (e) => {
            if (e.target.id === 'pet-tts-modal') {
                this.hideTTSModal();
            }
        });
        
        // TTS 활성화/비활성화
        document.getElementById('pet-tts-enabled').addEventListener('change', (e) => {
            this.currentSettings.is_enabled = e.target.checked;
            this.updateTTSButton();
        });
        
        // TTS 제공업체 변경
        document.getElementById('pet-tts-provider').addEventListener('change', (e) => {
            this.currentSettings.provider = e.target.value;
            // 제공업체 변경 시 음성 목록 다시 로드
            this.loadAvailableVoices(e.target.value);
            // 제공업체별 UI 업데이트
            this.updateProviderSpecificUI(e.target.value);
        });
        
        // 슬라이더 이벤트들
        document.getElementById('pet-speed-range').addEventListener('input', (e) => {
            const value = parseInt(e.target.value);
            this.currentSettings.speed = value;
            document.getElementById('pet-speed-value').textContent = value;
        });
        
        document.getElementById('pet-pitch-range').addEventListener('input', (e) => {
            const value = parseInt(e.target.value);
            this.currentSettings.pitch = value;
            document.getElementById('pet-pitch-value').textContent = value;
        });
        
        document.getElementById('pet-volume-range').addEventListener('input', (e) => {
            const value = parseInt(e.target.value);
            this.currentSettings.volume = value;
            document.getElementById('pet-volume-value').textContent = value;
        });
        
        // 감정 셀렉트
        document.getElementById('pet-emotion-select').addEventListener('change', (e) => {
            this.currentSettings.emotion = parseInt(e.target.value);
        });
        
        // 테스트 버튼
        document.getElementById('test-pet-tts').addEventListener('click', () => {
            this.testPetTTS();
        });
        
        // 저장 버튼
        document.getElementById('save-pet-tts-settings').addEventListener('click', () => {
            this.savePetSettings();
        });
    }
    
    async loadAvailableVoices(provider = null) {
        try {
            let url = '/api/tts/voices';
            if (provider) {
                url += `?provider=${provider}`;
            }
            
            console.log('음성 목록 로드 시도:', url);
            const response = await fetch(url);
            const data = await response.json();
            
            console.log('음성 목록 응답:', data);
            
            if (data.success) {
                this.availableVoices = data.voices;
                console.log('로드된 음성 목록:', this.availableVoices);
                this.renderVoiceCategories();
            } else {
                console.error('음성 목록 로드 실패 - 서버 응답:', data);
            }
        } catch (error) {
            console.error('음성 목록 로드 실패:', error);
        }
    }
    
    renderVoiceCategories() {
        const container = document.getElementById('voice-categories');
        if (!container) {
            console.error('voice-categories 컨테이너를 찾을 수 없습니다.');
            return;
        }
        
        console.log('음성 카테고리 렌더링 시작:', this.availableVoices);
        container.innerHTML = '';
        
        if (!this.availableVoices || Object.keys(this.availableVoices).length === 0) {
            console.warn('사용 가능한 음성이 없습니다.');
            container.innerHTML = '<p class="text-gray-500 text-sm">사용 가능한 음성이 없습니다.</p>';
            return;
        }
        
        Object.entries(this.availableVoices).forEach(([category, voices]) => {
            console.log('카테고리 렌더링:', category, voices);
            const categoryDiv = document.createElement('div');
            categoryDiv.className = 'border border-gray-200 rounded-lg p-3';
            
            const categoryTitle = this.getCategoryTitle(category);
            categoryDiv.innerHTML = `
                <h4 class="text-sm font-medium text-gray-700 mb-2">${categoryTitle}</h4>
                <div class="grid grid-cols-1 gap-1">
                    ${Object.entries(voices).map(([key, name]) => `
                        <label class="flex items-center cursor-pointer hover:bg-gray-50 p-1 rounded">
                            <input type="radio" name="pet-voice" value="${key}" class="mr-2">
                            <span class="text-sm">${name}</span>
                        </label>
                    `).join('')}
                </div>
            `;
            
            container.appendChild(categoryDiv);
        });
        
        // 라디오 버튼 이벤트 추가
        container.addEventListener('change', (e) => {
            if (e.target.name === 'pet-voice') {
                this.currentSettings.voice_id = e.target.value;
            }
        });
    }
    
    getCategoryTitle(category) {
        const titles = {
            'korean_female': '한국어 여성',
            'korean_male': '한국어 남성',
            'child_like': '귀여운 목소리',
            'international': '외국어'
        };
        return titles[category] || category;
    }
    
    updateProviderSpecificUI(provider) {
        const pitchContainer = document.getElementById('pet-pitch-range').closest('div');
        const volumeContainer = document.getElementById('pet-volume-range').closest('div');
        const emotionContainer = document.getElementById('pet-emotion-select').closest('div');
        
        if (provider === 'gemini') {
            // Gemini는 pitch, volume, emotion 지원하지 않음
            if (pitchContainer) pitchContainer.style.display = 'none';
            if (volumeContainer) volumeContainer.style.display = 'none';
            if (emotionContainer) emotionContainer.style.display = 'none';
        } else {
            // OpenAI는 모든 설정 지원
            if (pitchContainer) pitchContainer.style.display = 'block';
            if (volumeContainer) volumeContainer.style.display = 'block';
            if (emotionContainer) emotionContainer.style.display = 'block';
        }
    }
    
    updateModalContent() {
        if (!this.currentSettings.pet_name) return;
        
        // 펫 이름 업데이트
        document.getElementById('modal-pet-name').textContent = `${this.currentSettings.pet_name}의 음성 설정`;
        
        // 설정값들 업데이트
        document.getElementById('pet-tts-enabled').checked = this.currentSettings.is_enabled;
        document.getElementById('pet-tts-provider').value = this.currentSettings.provider || 'openai';
        document.getElementById('pet-speed-range').value = this.currentSettings.speed;
        document.getElementById('pet-speed-value').textContent = this.currentSettings.speed;
        document.getElementById('pet-pitch-range').value = this.currentSettings.pitch;
        document.getElementById('pet-pitch-value').textContent = this.currentSettings.pitch;
        document.getElementById('pet-volume-range').value = this.currentSettings.volume;
        document.getElementById('pet-volume-value').textContent = this.currentSettings.volume;
        document.getElementById('pet-emotion-select').value = this.currentSettings.emotion;
        
        // 선택된 음성 라디오 버튼 체크
        const voiceRadio = document.querySelector(`input[name="pet-voice"][value="${this.currentSettings.voice_id}"]`);
        if (voiceRadio) {
            voiceRadio.checked = true;
        }
        
        // 제공업체별 UI 업데이트
        this.updateProviderSpecificUI(this.currentSettings.provider || 'openai');
    }
    
    updateTTSButton() {
       const button = document.getElementById('tts-settings-btn');
       if (button && this.currentSettings) {
           const icon = button.querySelector('i');
           const isEnabled = this.currentSettings.is_enabled;
           icon.className = `fas fa-volume-${isEnabled ? 'up' : 'mute'} text-gray-600`;
           
           // 툴팁도 업데이트
           button.title = `${this.currentSettings.pet_name || '반려동물'}의 TTS 설정 ${isEnabled ? '(활성화)' : '(비활성화)'}`;
       }
   }
   
   showTTSModal() {
       document.getElementById('pet-tts-modal').classList.remove('hidden');
       document.getElementById('pet-tts-modal').classList.add('flex');
   }
   
   hideTTSModal() {
       document.getElementById('pet-tts-modal').classList.add('hidden');
       document.getElementById('pet-tts-modal').classList.remove('flex');
   }
   
   async testPetTTS() {
       if (!this.currentPetId) {
           this.showToast('반려동물을 선택해주세요.', 'warning');
           return;
       }
       
       const testText = `안녕! 나는 ${this.currentSettings.pet_name || '반려동물'}이야! 이것은 TTS 테스트야!`;
       await this.playPetTTS(testText);
   }
   
   async savePetSettings() {
       if (!this.currentPetId) {
           this.showToast('반려동물을 선택해주세요.', 'warning');
           return;
       }
       
       try {
           const response = await fetch(`/api/tts/pet-settings/${this.currentPetId}`, {
               method: 'PUT',
               headers: {
                   'Content-Type': 'application/json',
               },
               body: JSON.stringify({
                   provider: this.currentSettings.provider,
                   is_enabled: this.currentSettings.is_enabled,
                   voice_id: this.currentSettings.voice_id,
                   speed: this.currentSettings.speed,
                   pitch: this.currentSettings.pitch,
                   emotion: this.currentSettings.emotion,
                   volume: this.currentSettings.volume
               })
           });
           
           const data = await response.json();
           
           if (data.success) {
               this.currentSettings = data.settings;
               this.updateTTSButton();
               this.hideTTSModal();
               this.showToast('TTS 설정이 저장되었습니다.', 'success');
           } else {
               this.showToast(data.error || '설정 저장에 실패했습니다.', 'error');
           }
       } catch (error) {
           console.error('TTS 설정 저장 실패:', error);
           this.showToast('설정 저장 중 오류가 발생했습니다.', 'error');
       }
   }
   
   async playPetTTS(text) {
       if (!this.currentPetId || this.isPlaying) return;
       
       // TTS가 비활성화된 경우 바로 종료
       if (!this.currentSettings.is_enabled) {
           return;
       }
       
       try {
           this.isPlaying = true;
           
           // TTS 버튼에 로딩 상태 표시
           this.updateTTSButtonState('loading');
           
           console.log('TTS 생성 요청:', text.length, '글자');
           const startTime = performance.now();
           
           const response = await fetch('/api/tts/generate-for-pet', {
               method: 'POST',
               headers: {
                   'Content-Type': 'application/json',
               },
               body: JSON.stringify({
                   text: text,
                   pet_id: this.currentPetId
               })
           });
           
           const data = await response.json();
           
           if (data.success && data.audio) {
               const endTime = performance.now();
               console.log(`TTS 생성 완료: ${Math.round(endTime - startTime)}ms`);
               
               // Base64를 Blob으로 직접 변환 (성능 최적화)
               const byteCharacters = atob(data.audio);
               const byteNumbers = new Array(byteCharacters.length);
               for (let i = 0; i < byteCharacters.length; i++) {
                   byteNumbers[i] = byteCharacters.charCodeAt(i);
               }
               const byteArray = new Uint8Array(byteNumbers);
               const blob = new Blob([byteArray], { type: 'audio/mp3' });
               const audioUrl = URL.createObjectURL(blob);
               
               const audio = new Audio(audioUrl);
               
               // 오디오 이벤트 리스너 추가
               const cleanup = () => {
                   URL.revokeObjectURL(audioUrl);
                   this.isPlaying = false;
                   this.updateTTSButtonState('idle');
               };
               
               audio.addEventListener('ended', cleanup);
               audio.addEventListener('error', () => {
                   console.error('오디오 재생 실패');
                   cleanup();
               });
               
               // 즉시 재생 시도
               try {
                   await audio.play();
                   console.log('TTS 재생 시작');
               } catch (playError) {
                   console.error('오디오 재생 실패:', playError);
                   cleanup();
               }
           } else {
               this.isPlaying = false;
               this.updateTTSButtonState('idle');
               if (data.error) {
                   console.log('TTS 알림:', data.error);
               }
           }
       } catch (error) {
           this.isPlaying = false;
           this.updateTTSButtonState('error');
           console.error('TTS 재생 실패:', error);
       }
   }
   
   updateTTSButtonState(state) {
       const button = document.getElementById('tts-settings-btn');
       if (!button) return;
       
       const icon = button.querySelector('i');
       if (!icon) return;
       
       switch (state) {
           case 'loading':
               icon.className = 'fas fa-spinner fa-spin text-blue-500';
               button.title = 'TTS 생성 중...';
               break;
           case 'error':
               icon.className = 'fas fa-exclamation-triangle text-red-500';
               button.title = 'TTS 오류 발생';
               setTimeout(() => this.updateTTSButtonState('idle'), 2000);
               break;
           case 'idle':
           default:
               const isEnabled = this.currentSettings?.is_enabled;
               icon.className = `fas fa-volume-${isEnabled ? 'up' : 'mute'} text-gray-600`;
               button.title = `${this.currentSettings?.pet_name || '반려동물'}의 TTS 설정 ${isEnabled ? '(활성화)' : '(비활성화)'}`;
               break;
       }
   }
   
   showToast(message, type = 'info') {
       const toastColors = {
           'success': 'bg-green-500',
           'error': 'bg-red-500',
           'warning': 'bg-yellow-500',
           'info': 'bg-blue-500'
       };
       
       const toast = document.createElement('div');
       toast.className = `fixed bottom-4 right-4 ${toastColors[type]} text-white px-4 py-2 rounded-lg shadow-lg z-50 opacity-0 transition-opacity duration-300`;
       toast.textContent = message;
       
       document.body.appendChild(toast);
       
       // 페이드 인
       setTimeout(() => {
           toast.classList.remove('opacity-0');
       }, 100);
       
       // 페이드 아웃 후 제거
       setTimeout(() => {
           toast.classList.add('opacity-0');
           setTimeout(() => {
               toast.remove();
           }, 300);
       }, 3000);
   }
}

// 전역 TTS 매니저 인스턴스
window.petTTSManager = null;

// 페이지 로드 후 TTS 매니저 초기화
document.addEventListener('DOMContentLoaded', () => {
   window.petTTSManager = new PetTTSManager();
});