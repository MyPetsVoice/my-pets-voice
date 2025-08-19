// 현재 선택된 반려동물
let currentChatPet = null;

// 알림 상태 관리
let notificationData = [
    {
        id: 1,
        type: 'like',
        title: '새로운 좋아요',
        message: '누군가가 당신의 게시물을 좋아합니다',
        time: '5분 전',
        read: false,
        icon: 'fas fa-heart',
        iconColor: 'bg-primary-500'
    },
    {
        id: 2,
        type: 'comment',
        title: '새로운 댓글',
        message: '멍멍이가 너무 귀여워요!',
        time: '1시간 전',
        read: false,
        icon: 'fas fa-comment',
        iconColor: 'bg-secondary-500'
    },
    {
        id: 3,
        type: 'follow',
        title: '새로운 팔로워',
        message: '김철수님이 당신을 팔로우했습니다',
        time: '2시간 전',
        read: true,
        icon: 'fas fa-user-plus',
        iconColor: 'bg-green-500'
    }
];

// 알림 드롭다운 토글
function toggleNotifications() {
    const dropdown = document.getElementById('notification-dropdown');
    dropdown.classList.toggle('hidden');
    
    // 다른 곳 클릭 시 드롭다운 닫기
    if (!dropdown.classList.contains('hidden')) {
        document.addEventListener('click', closeNotificationOnOutsideClick);
    } else {
        document.removeEventListener('click', closeNotificationOnOutsideClick);
    }
}

// 외부 클릭 시 알림 드롭다운 닫기
function closeNotificationOnOutsideClick(event) {
    const dropdown = document.getElementById('notification-dropdown');
    const button = document.getElementById('notification-btn');
    
    if (!dropdown.contains(event.target) && !button.contains(event.target)) {
        dropdown.classList.add('hidden');
        document.removeEventListener('click', closeNotificationOnOutsideClick);
    }
}

// 읽지 않은 알림 개수 업데이트
function updateNotificationBadge() {
    const badge = document.getElementById('notification-badge');
    const unreadCount = notificationData.filter(notification => !notification.read).length;
    
    if (unreadCount > 0) {
        badge.textContent = unreadCount;
        badge.style.display = 'flex';
    } else {
        badge.style.display = 'none';
    }
}

// 모든 알림 읽음 처리
function markAllAsRead() {
    notificationData.forEach(notification => {
        notification.read = true;
    });
    updateNotificationBadge();
    renderNotifications();
}

// 알림 렌더링
function renderNotifications() {
    const container = document.querySelector('#notification-dropdown .max-h-96');
    container.innerHTML = '';
    
    notificationData.forEach(notification => {
        const notificationElement = document.createElement('div');
        notificationElement.className = 'notification-item p-4 border-b border-gray-100 hover:bg-gray-50 cursor-pointer';
        notificationElement.innerHTML = `
            <div class="flex items-start space-x-3">
                <div class="flex-shrink-0">
                    <div class="w-8 h-8 ${notification.iconColor} rounded-full flex items-center justify-center">
                        <i class="${notification.icon} text-white text-sm"></i>
                    </div>
                </div>
                <div class="flex-1 min-w-0">
                    <p class="text-sm font-medium text-gray-900">${notification.title}</p>
                    <p class="text-sm text-gray-500">${notification.message}</p>
                    <p class="text-xs text-gray-400 mt-1">${notification.time}</p>
                </div>
                ${!notification.read ? '<div class="w-2 h-2 bg-blue-500 rounded-full"></div>' : ''}
            </div>
        `;
        container.appendChild(notificationElement);
    });
}

// 사용자 메뉴 토글
function toggleUserMenu() {
    const userMenu = document.getElementById('user-menu');
    userMenu.classList.toggle('active');
}

// 모바일 메뉴 토글
function toggleMobileMenu() {
    const navMenu = document.getElementById('nav-menu');
    navMenu.classList.toggle('active');
}

// 페이지 로드 시 초기화
document.addEventListener('DOMContentLoaded', function() {
    updateNotificationBadge();
    renderNotifications();
    
    // "모두 읽음" 버튼 이벤트 리스너 추가
    const markAllReadBtn = document.querySelector('#notification-dropdown .border-b button');
    if (markAllReadBtn) {
        markAllReadBtn.addEventListener('click', markAllAsRead);
    }
});
