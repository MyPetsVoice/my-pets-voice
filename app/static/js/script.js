// 메인 페이지 JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // 폼 유효성 검사
    const form = document.getElementById('petForm');
    if (form) {
        form.addEventListener('submit', function(e) {
            if (!validateForm()) {
                e.preventDefault();
            }
        });
    }
    
    // 실시간 입력 제한
    setupInputLimits();
    
    // 툴팁 및 도움말
    setupTooltips();
});

// 폼 유효성 검사
function validateForm() {
    const requiredFields = ['name', 'species', 'age', 'gender', 'owner_call', 'speech_style'];
    let isValid = true;
    
    // 필수 필드 검사
    requiredFields.forEach(fieldName => {
        const field = document.querySelector(`[name="${fieldName}"]`);
        if (!field || !field.value.trim()) {
            showFieldError(field, '이 필드는 필수입니다.');
            isValid = false;
        } else {
            clearFieldError(field);
        }
    });
    
    // 나이 범위 검사
    const age = document.querySelector('[name="age"]');
    if (age && age.value) {
        const ageValue = parseInt(age.value);
        if (ageValue < 0 || ageValue > 30) {
            showFieldError(age, '나이는 0-30 사이의 값이어야 합니다.');
            isValid = false;
        }
    }
    
    // 성격 선택 검사 (최소 1개)
    const personalityChecked = document.querySelectorAll('input[name="personality"]:checked');
    if (personalityChecked.length === 0) {
        showAlert('성격을 최소 1개 이상 선택해주세요.', 'warning');
        isValid = false;
    }
    
    // 기타 종류 선택 시 품종 입력 검사
    const species = document.querySelector('[name="species"]');
    const customBreed = document.getElementById('customBreed');
    if (species && species.value === '기타' && customBreed && !customBreed.value.trim()) {
        showFieldError(customBreed, '기타 종류를 선택하신 경우 품종을 직접 입력해주세요.');
        isValid = false;
    }
    
    return isValid;
}

// 필드 에러 표시
function showFieldError(field, message) {
    clearFieldError(field);
    
    field.classList.add('is-invalid');
    
    const errorDiv = document.createElement('div');
    errorDiv.className = 'invalid-feedback';
    errorDiv.textContent = message;
    
    field.parentNode.appendChild(errorDiv);
}

// 필드 에러 제거
function clearFieldError(field) {
    if (field) {
        field.classList.remove('is-invalid');
        const errorDiv = field.parentNode.querySelector('.invalid-feedback');
        if (errorDiv) {
            errorDiv.remove();
        }
    }
}

// 알림 표시
function showAlert(message, type = 'info') {
    // 기존 알림 제거
    const existingAlert = document.querySelector('.custom-alert');
    if (existingAlert) {
        existingAlert.remove();
    }
    
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show custom-alert`;
    alertDiv.style.position = 'fixed';
    alertDiv.style.top = '20px';
    alertDiv.style.right = '20px';
    alertDiv.style.zIndex = '9999';
    alertDiv.style.minWidth = '300px';
    
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    document.body.appendChild(alertDiv);
    
    // 5초 후 자동 제거
    setTimeout(() => {
        if (alertDiv.parentNode) {
            alertDiv.remove();
        }
    }, 5000);
}

// 입력 제한 설정
function setupInputLimits() {
    // 이름 필드 - 특수문자 제한
    const nameField = document.querySelector('[name="name"]');
    if (nameField) {
        nameField.addEventListener('input', function() {
            this.value = this.value.replace(/[^a-zA-Z가-힣0-9\s]/g, '');
            if (this.value.length > 20) {
                this.value = this.value.substring(0, 20);
            }
        });
    }
    
    // 호칭 필드 - 길이 제한
    const ownerCallField = document.querySelector('[name="owner_call"]');
    if (ownerCallField) {
        ownerCallField.addEventListener('input', function() {
            if (this.value.length > 10) {
                this.value = this.value.substring(0, 10);
            }
        });
    }
    
    // 텍스트 영역 글자 수 제한
    const textareas = document.querySelectorAll('textarea');
    textareas.forEach(textarea => {
        const maxLength = 200;
        
        // 글자 수 표시 추가
        const counter = document.createElement('small');
        counter.className = 'text-muted float-end';
        counter.style.marginTop = '5px';
        textarea.parentNode.appendChild(counter);
        
        function updateCounter() {
            const current = textarea.value.length;
            counter.textContent = `${current}/${maxLength}`;
            
            if (current > maxLength * 0.9) {
                counter.className = 'text-warning float-end';
            } else {
                counter.className = 'text-muted float-end';
            }
            
            if (current > maxLength) {
                textarea.value = textarea.value.substring(0, maxLength);
                counter.textContent = `${maxLength}/${maxLength}`;
                counter.className = 'text-danger float-end';
            }
        }
        
        textarea.addEventListener('input', updateCounter);
        updateCounter(); // 초기 설정
    });
}

// 툴팁 설정
function setupTooltips() {
    // Bootstrap 툴팁 초기화
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // 커스텀 도움말 추가
    addHelpTooltips();
}

// 도움말 툴팁 추가
function addHelpTooltips() {
    const helpTexts = {
        'personality': '반려동물의 성격을 잘 나타내는 특성들을 선택하세요. 여러 개 선택 가능합니다.',
        'speech_style': '반려동물이 어떤 말투로 대화할지 선택하세요.',
        'likes': '반려동물이 좋아하는 것들을 쉼표로 구분해서 입력하세요.',
        'dislikes': '반려동물이 싫어하는 것들을 쉼표로 구분해서 입력하세요.',
        'habits': '반려동물의 특별한 습관이나 행동을 입력하세요.',
        'special_notes': '외형, 가족관계 등 대화에서 특별히 언급되었으면 하는 내용을 자유롭게 작성하세요.'
    };
    
    Object.keys(helpTexts).forEach(fieldName => {
        const field = document.querySelector(`[name="${fieldName}"]`) || 
                     document.querySelector(`label[for="${fieldName}"]`);
        if (field) {
            const helpIcon = document.createElement('i');
            helpIcon.className = 'fas fa-question-circle text-muted ms-1';
            helpIcon.style.cursor = 'help';
            helpIcon.setAttribute('data-bs-toggle', 'tooltip');
            helpIcon.setAttribute('data-bs-placement', 'top');
            helpIcon.setAttribute('title', helpTexts[fieldName]);
            
            const label = document.querySelector(`label[for="${fieldName}"]`);
            if (label) {
                label.appendChild(helpIcon);
            }
        }
    });
}

// 성격 선택 개선
document.addEventListener('DOMContentLoaded', function() {
    const personalityLabels = document.querySelectorAll('.personality-tags label');
    personalityLabels.forEach(label => {
        label.addEventListener('click', function() {
            // 선택 효과 애니메이션
            this.style.transform = 'scale(0.95)';
            setTimeout(() => {
                this.style.transform = 'scale(1)';
            }, 100);
        });
    });
});

// 로딩 상태 관리
function showLoading() {
    const submitBtn = document.querySelector('button[type="submit"]');
    if (submitBtn) {
        submitBtn.disabled = true;
        submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>처리 중...';
    }
}

function hideLoading() {
    const submitBtn = document.querySelector('button[type="submit"]');
    if (submitBtn) {
        submitBtn.disabled = false;
        submitBtn.innerHTML = '<i class="fas fa-comments me-2"></i>대화 시작하기';
    }
}

// 브라우저 호환성 체크
function checkBrowserCompatibility() {
    const isModernBrowser = 'fetch' in window && 'Promise' in window;
    if (!isModernBrowser) {
        showAlert('이 웹사이트는 최신 브라우저에서 더 잘 동작합니다. 브라우저를 업데이트해주세요.', 'warning');
    }
}

// 초기화
document.addEventListener('DOMContentLoaded', function() {
    checkBrowserCompatibility();
});