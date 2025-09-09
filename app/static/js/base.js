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
    navMenu.classList.toggle('right-0');
    navMenu.classList.toggle('w-56'); // 가로 너비 제한 (14rem = 224px)
    navMenu.classList.toggle('bg-white');
    navMenu.classList.toggle('shadow-lg');
    navMenu.classList.toggle('rounded-b-xl');
    navMenu.classList.toggle('p-4');
    navMenu.classList.toggle('z-50');
    navMenu.classList.toggle('space-x-0'); // 가로 간격 제거
    navMenu.classList.toggle('space-y-2'); // 세로 간격 추가
    
    // 메뉴가 열릴 때 외부 클릭 리스너 추가
    if (isHidden) {
        setTimeout(() => {
            document.addEventListener('click', closeMobileMenuOnOutsideClick);
        }, 100);
    } else {
        document.removeEventListener('click', closeMobileMenuOnOutsideClick);
    }
}

// 모바일 메뉴에 페이지 링크 추가
function addMobileMenuContent() {
    const navMenu = document.getElementById('nav-menu');
    const existingMobileContent = navMenu.querySelector('.mobile-menu-links');
    
    // 이미 추가된 콘텐츠가 있으면 제거
    if (existingMobileContent) {
        existingMobileContent.remove();
    }
    
    // 현재 페이지 경로 확인
    const currentPath = window.location.pathname;
    
    // 모바일 메뉴 링크들 생성
    const mobileLinks = document.createElement('div');
    mobileLinks.className = 'mobile-menu-links space-y-2';
    
    // 페이지 링크들
    const links = [
        { href: '/chat', text: '반려동물과 대화하기', endpoint: 'chat' },
        { href: '/diary', text: '너의 일기장', endpoint: 'diary' },
        { href: '/dailycare', text: '데일리 케어', endpoint: 'dailycare' },
        { href: '/mypage', text: '마이페이지', endpoint: 'mypage' }
    ];
    
    links.forEach(link => {
        const linkElement = document.createElement('a');
        linkElement.href = link.href;
        linkElement.textContent = link.text;
        
        // 현재 페이지인지 확인
        const isActive = currentPath.includes(link.endpoint);
        linkElement.className = `block px-4 py-3 rounded-lg font-medium transition-all duration-300 ${
            isActive 
                ? 'text-white bg-gradient-to-r from-orange-400 to-red-400' 
                : 'text-gray-700 hover:text-white hover:bg-gradient-to-r hover:from-orange-400 hover:to-red-400'
        }`;
        
        mobileLinks.appendChild(linkElement);
    });
    
    navMenu.appendChild(mobileLinks);
}

// 모바일 사용자 메뉴 토글 (네비게이션 바용)
function toggleMobileUserMenuNav() {
    const dropdown = document.getElementById('mobile-user-dropdown-nav');
    const arrow = document.getElementById('mobile-user-menu-nav-arrow');
    
    if (dropdown && arrow) {
        dropdown.classList.toggle('hidden');
        arrow.classList.toggle('rotate-180');
        
        // 드롭다운이 열릴 때 외부 클릭 리스너 추가
        if (!dropdown.classList.contains('hidden')) {
            setTimeout(() => {
                document.addEventListener('click', closeMobileUserMenuNavOnOutsideClick);
            }, 100);
        } else {
            document.removeEventListener('click', closeMobileUserMenuNavOnOutsideClick);
        }
    }
}

// 외부 클릭 시 모바일 네비 사용자 메뉴 닫기
function closeMobileUserMenuNavOnOutsideClick(event) {
    const dropdown = document.getElementById('mobile-user-dropdown-nav');
    const userMenu = document.getElementById('mobile-user-menu-nav');
    
    if (userMenu && !userMenu.contains(event.target)) {
        dropdown.classList.add('hidden');
        document.getElementById('mobile-user-menu-nav-arrow').classList.remove('rotate-180');
        document.removeEventListener('click', closeMobileUserMenuNavOnOutsideClick);
    }
}

// 모바일 사용자 메뉴 토글 (드롭다운 메뉴용 - 제거됨)
function toggleMobileUserMenu() {
    // 이 함수는 더 이상 필요하지 않음
}

// 모바일 메뉴 닫기
function closeMobileMenu() {
    const navMenu = document.getElementById('nav-menu');
    if (!navMenu.classList.contains('hidden')) {
        navMenu.classList.add('hidden');
        navMenu.classList.remove('flex', 'flex-col', 'absolute', 'top-full', 'right-0', 'w-56', 'bg-white', 'shadow-lg', 'rounded-b-xl', 'p-4', 'z-50', 'space-x-0', 'space-y-2');
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
