// // 현재 선택된 반려동물
let currentChatPet = null;

// 사용자 메뉴 토글
function toggleUserMenu() {
    const dropdown = document.getElementById('user-dropdown');
    const arrow = document.getElementById('user-menu-arrow');
    
    dropdown.classList.toggle('hidden');
    arrow.classList.toggle('rotate-180');
    
    // 드롭다운이 열릴 때 외부 클릭 리스너 추가
    if (!dropdown.classList.contains('hidden')) {
        setTimeout(() => {
            document.addEventListener('click', closeUserMenuOnOutsideClick);
        }, 100);
    } else {
        document.removeEventListener('click', closeUserMenuOnOutsideClick);
    }
}

// 외부 클릭 시 사용자 메뉴 닫기
function closeUserMenuOnOutsideClick(event) {
    const dropdown = document.getElementById('user-dropdown');
    const userMenu = document.getElementById('user-menu');
    
    if (!userMenu.contains(event.target)) {
        dropdown.classList.add('hidden');
        document.getElementById('user-menu-arrow').classList.remove('rotate-180');
        document.removeEventListener('click', closeUserMenuOnOutsideClick);
    }
}

// 모바일 메뉴 토글
function toggleMobileMenu() {
    const navMenu = document.getElementById('nav-menu');
    const isHidden = navMenu.classList.contains('hidden');
    
    // 메뉴가 열릴 때 모바일용 콘텐츠 추가
    if (isHidden) {
        addMobileMenuContent();
    }
    
    navMenu.classList.toggle('hidden');
    navMenu.classList.toggle('flex');
    navMenu.classList.toggle('flex-col');
    navMenu.classList.toggle('absolute');
    navMenu.classList.toggle('top-full');
    navMenu.classList.toggle('left-0');
    navMenu.classList.toggle('right-0');
    navMenu.classList.toggle('bg-white');
    navMenu.classList.toggle('shadow-lg');
    navMenu.classList.toggle('rounded-b-xl');
    navMenu.classList.toggle('p-5');
    navMenu.classList.toggle('z-50');
    
    // 메뉴가 열릴 때 외부 클릭 리스너 추가
    if (isHidden) {
        setTimeout(() => {
            document.addEventListener('click', closeMobileMenuOnOutsideClick);
        }, 100);
    } else {
        document.removeEventListener('click', closeMobileMenuOnOutsideClick);
    }
}

// 모바일 메뉴에 날씨와 사용자 정보 추가
function addMobileMenuContent() {
    const navMenu = document.getElementById('nav-menu');
    const existingMobileContent = navMenu.querySelector('.mobile-extra-content');
    
    // 이미 추가된 콘텐츠가 있으면 제거
    if (existingMobileContent) {
        existingMobileContent.remove();
    }
    
    // 사용자 정보와 날씨를 모바일 메뉴에 추가
    const mobileContent = document.createElement('div');
    mobileContent.className = 'mobile-extra-content border-t pt-4 mt-4';
    
    // 사용자 정보 또는 로그인 버튼
    const userSection = document.querySelector('#user-menu, a[href*="kakao_login"]');
    if (userSection) {
        const userInfo = userSection.cloneNode(true);
        // 모바일용 스타일 조정
        if (userInfo.id === 'user-menu') {
            userInfo.id = 'mobile-user-menu';
            const button = userInfo.querySelector('button');
            if (button) {
                button.className = 'w-full flex items-center space-x-2 px-3 py-2 rounded-lg bg-gradient-to-r from-primary-50 to-secondary-50 border border-primary-200';
                button.setAttribute('onclick', 'toggleMobileUserMenu()');
            }
            // 드롭다운을 바로 보여주는 스타일로 변경
            const dropdown = userInfo.querySelector('#user-dropdown');
            if (dropdown) {
                dropdown.id = 'mobile-user-dropdown';
                dropdown.className = 'hidden mt-2 w-full bg-gray-50 border border-gray-200 rounded-lg';
            }
        }
        mobileContent.appendChild(userInfo);
    }
    
    // 날씨 정보
    const weatherWidget = document.getElementById('weather');
    if (weatherWidget) {
        const weatherClone = weatherWidget.cloneNode(true);
        weatherClone.id = 'mobile-weather';
        weatherClone.className = 'mt-3';
        mobileContent.appendChild(weatherClone);
        
        // 모바일 날씨 위젯 초기화
        setTimeout(() => {
            if (window.initWeatherWidget) {
                initWeatherWidget('mobile-weather', '서울');
            }
        }, 100);
    }
    
    navMenu.appendChild(mobileContent);
}

// 모바일 사용자 메뉴 토글
function toggleMobileUserMenu() {
    const dropdown = document.getElementById('mobile-user-dropdown');
    if (dropdown) {
        dropdown.classList.toggle('hidden');
    }
}

// 모바일 메뉴 닫기
function closeMobileMenu() {
    const navMenu = document.getElementById('nav-menu');
    if (!navMenu.classList.contains('hidden')) {
        navMenu.classList.add('hidden');
        navMenu.classList.remove('flex', 'flex-col', 'absolute', 'top-full', 'left-0', 'right-0', 'bg-white', 'shadow-lg', 'rounded-b-xl', 'p-5', 'z-50');
        document.removeEventListener('click', closeMobileMenuOnOutsideClick);
    }
}

// 외부 클릭 시 모바일 메뉴 닫기
function closeMobileMenuOnOutsideClick(event) {
    const navMenu = document.getElementById('nav-menu');
    const menuButton = document.querySelector('button[onclick="toggleMobileMenu()"]');
    
    if (!navMenu.contains(event.target) && !menuButton.contains(event.target)) {
        closeMobileMenu();
    }
}
