// 탭 전환
function switchTab(event, tabName) {
  document
    .querySelectorAll(".nav-tab")
    .forEach((tab) => tab.classList.remove("active"));
  document
    .querySelectorAll(".tab-content")
    .forEach((content) => content.classList.remove("active"));

  event.target.classList.add("active");
  document.getElementById(tabName + "-tab").classList.add("active");
}
// // open modal
// function openModal(name) {
//   console.log(`##### name ${name}`);
//   fetch(`/api/dailycares/modal/${name}`)
//     .then((res) => {
//       if (!res.ok) throw new Error("네트워크 오류");
//       return res.text();
//     })
//     .then((html) => {
//       // console.log(`##### html ${html}`);
//       const modal = document.getElementById("common-modal");
//       const content = modal.querySelector("#modalContent");

//       content.innerHTML = html; // AJAX 내용 삽입
//       modal.classList.remove("hidden"); // 모달 표시

//       // 닫기 버튼 이벤트
//       const closeBtn = document.getElementById("modal-close-btn");
//       closeBtn.onclick = () => modal.classList.add("hidden");
//     })
//     .catch((err) => {
//       console.error("모달 불러오기 실패:", err);
//       alert("모달을 불러오지 못했습니다.");
//     });
// }

// // close modal
// function closeModal() {
//   document.getElementById("common-modal").classList.add("hidden");
// }
