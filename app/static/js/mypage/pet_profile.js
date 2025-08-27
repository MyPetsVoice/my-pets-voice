
// 동물 종류별 품종 데이터 - 서버에서 전달받은 데이터 사용
// 템플릿에서 전역 변수로 설정될 예정

// 종류 변경 시 품종 업데이트
document.getElementById('species').addEventListener('change', function() {
const species = this.value;
const breedSelect = document.getElementById('breed');
const customBreed = document.getElementById('customBreed');

breedSelect.innerHTML = '<option value="">선택하세요</option>';

if (species === '기타' || species === '') {
    if (species === '기타') {
        breedSelect.classList.add('d-none');
        customBreed.classList.remove('d-none');
    } else {
        breedSelect.classList.remove('d-none');
        customBreed.classList.add('d-none');
    }
    return;
}

breedSelect.classList.remove('d-none');
customBreed.classList.add('d-none');

if (animalsData[species]) {
    if (Array.isArray(animalsData[species])) {
        animalsData[species].forEach(breed => {
            const option = document.createElement('option');
            option.value = breed;
            option.textContent = breed;
            breedSelect.appendChild(option);
        });
    } else {
        Object.values(animalsData[species]).flat().forEach(breed => {
            const option = document.createElement('option');
            option.value = breed;
            option.textContent = breed;
            breedSelect.appendChild(option);
        });
    }
}
});

// 폼 제출
document.getElementById('petForm').addEventListener('submit', function(e) {
e.preventDefault();

const formData = new FormData(this);
const customBreed = document.getElementById('customBreed').value;

if (document.getElementById('species').value === '기타' && customBreed) {
    formData.set('breed', customBreed);
}

fetch('/create_pet', {
    method: 'POST',
    body: formData
})
.then(response => response.json())
.then(data => {
    if (data.success) {
        window.location.href = '/chat';
    } else {
        alert('오류가 발생했습니다: ' + (data.error || '알 수 없는 오류'));
    }
})
.catch(error => {
    console.error('Error:', error);
    alert('서버 오류가 발생했습니다.');
});
});