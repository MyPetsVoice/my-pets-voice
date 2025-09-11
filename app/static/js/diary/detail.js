// detail.js

// 전역 변수
let diaryData = null;
let currentPhotoIndex = 0;
let photos = [];

// 페이지 로드 시 초기화
document.addEventListener("DOMContentLoaded", async function () {
  await loadDiaryDetail();
});

// 일기 상세 정보 로드
async function loadDiaryDetail() {
  const diaryId = window.DIARY_ID;

  const response = await fetch(`/api/diary/detail/${diaryId}`);
  const data = await response.json();

  if (data.success) {
    diaryData = data.diary;
    displayDiary(diaryData);

    // 로딩 상태 숨기고 콘텐츠 표시
    document.getElementById("loadingState").classList.add("hidden");
    document.getElementById("diaryContent").classList.remove("hidden");
  } else {
    // 에러 상태 표시
    document.getElementById("loadingState").classList.add("hidden");
    document.getElementById("errorState").classList.remove("hidden");
  }
}

// 일기 내용 표시
function displayDiary(diary) {
  // 기본 정보 표시
  document.getElementById("diaryTitle").textContent = diary.title;
  document.getElementById("diaryDate").textContent = formatDate(
    diary.diary_date
  );

  // 펫 정보 표시 (임시 - 나중에 실제 펫 정보 API로 수정)
  const petEmoji = "🐕"; //프로필? 넣기
  const petName = "반려동물"; // 임시
  document.getElementById("petEmoji").textContent = petEmoji;
  document.getElementById("petInfo").textContent = `${petName}의 일기`;
  document.getElementById("petName").textContent = petName;

  // 날씨, 기분 표시
  if (diary.weather) {
    document.getElementById("weatherInfo").textContent = diary.weather;
  } else {
    document.getElementById("weatherInfo").style.display = "none";
  }

  if (diary.mood) {
    document.getElementById("moodInfo").textContent = diary.mood;
  } else {
    document.getElementById("moodInfo").style.display = "none";
  }

  // 사진 표시
  if (diary.photos && diary.photos.length > 0) {
    displayPhotoGallery(diary.photos);
  } else {
    // 사진이 없으면 갤러리 섹션 숨기기
    document.getElementById("photoGallery").classList.add("hidden");
  }

  // 일기 내용 표시
  displayDiaryContent(diary);
}

// 사진 표시
function displayPhotoGallery(photoList) {
  photos = photoList;
  const photoGrid = document.getElementById("photoGrid");

  photoGrid.innerHTML = photoList
    .map(
      (photo, index) => `
        <div class="photo-item" onclick="openImageModal(${index})">
            <img src="${photo.photo_url}" alt="" loading="lazy" onerror="this.parentElement.style.display='none'">
        </div>
    `
    )
    .join("");

  document.getElementById("photoGallery").classList.remove("hidden");
}

// 일기 내용 표시
function displayDiaryContent(diary) {
  // AI가 변환한 내용
  if (diary.content_ai) {
    document.getElementById("aiContentText").textContent = diary.content_ai;
    document.getElementById("aiContent").classList.remove("hidden");
  }
}

// 일기 삭제
async function deleteDiary() {
  if (
    !confirm(
      "정말로 이 일기를 삭제하시겠습니까?\n삭제된 일기는 복구할 수 없습니다."
    )
  ) {
    return;
  }

  const diaryId = window.DIARY_ID;

  const response = await fetch(`/api/diary/delete/${diaryId}`, {
    method: "DELETE",
  });

  if (response.ok) {
    alert("일기가 삭제되었습니다.");
    window.location.href = "/diary/";
  } else {
    alert("삭제에 실패했습니다.");
  }
}

// 이미지 모달 열기
function openImageModal(photoIndex) {
  if (photos.length === 0) return;

  currentPhotoIndex = photoIndex;
  const modal = document.getElementById("imageModal");
  const modalImage = document.getElementById("modalImage");

  modalImage.src = photos[currentPhotoIndex].photo_url;
  modal.classList.remove("hidden");
  modal.classList.add("show");

  // ESC 키로 모달 닫기
  document.addEventListener("keydown", handleModalKeydown);

  // 내비게이션 버튼 표시/숨김
  updateNavigationButtons();
}

// 이미지 모달 닫기
function closeImageModal() {
  const modal = document.getElementById("imageModal");
  modal.classList.add("hidden");
  modal.classList.remove("show");

  // 키보드 이벤트 리스너 제거
  document.removeEventListener("keydown", handleModalKeydown);
}

// 이전 이미지
function previousImage() {
  if (currentPhotoIndex > 0) {
    currentPhotoIndex--;
    document.getElementById("modalImage").src =
      photos[currentPhotoIndex].photo_url;
    updateNavigationButtons();
  }
}

// 다음 이미지
function nextImage() {
  if (currentPhotoIndex < photos.length - 1) {
    currentPhotoIndex++;
    document.getElementById("modalImage").src =
      photos[currentPhotoIndex].photo_url;
    updateNavigationButtons();
  }
}

// 내비게이션 버튼 업데이트
function updateNavigationButtons() {
  const prevBtn = document.getElementById("prevImageBtn");
  const nextBtn = document.getElementById("nextImageBtn");

  prevBtn.style.display = currentPhotoIndex > 0 ? "flex" : "none";
  nextBtn.style.display =
    currentPhotoIndex < photos.length - 1 ? "flex" : "none";
}

// 모달 키보드 이벤트
function handleModalKeydown(event) {
  switch (event.key) {
    case "Escape":
      closeImageModal();
      break;
    case "ArrowLeft":
      previousImage();
      break;
    case "ArrowRight":
      nextImage();
      break;
  }
}

// 날짜
function formatDate(dateString) {
  const date = new Date(dateString);
  const year = date.getFullYear();
  const month = String(date.getMonth() + 1).padStart(2, "0");
  const day = String(date.getDate()).padStart(2, "0");
  const weekdays = ["일", "월", "화", "수", "목", "금", "토"];
  const weekday = weekdays[date.getDay()];

  return `${year}년 ${month}월 ${day}일 (${weekday})`;
}

// 모달 외부 클릭해서 닫기
document.addEventListener("DOMContentLoaded", function () {
  const modal = document.getElementById("imageModal");
  modal.addEventListener("click", function (event) {
    if (event.target === modal) {
      closeImageModal();
    }
  });
});
