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
