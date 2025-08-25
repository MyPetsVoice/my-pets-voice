let pet_id = null;

document.addEventListener("DOMContentLoaded", () => {
  pet_id = Number(document.getElementById("modal-pet-id").value);
  console.log("pet_id loaded:", pet_id);
});

const save_btn = document.getElementById("save_medication_button");
save_btn.addEventListener("click", () => {
  console.log("click button");
  saveMedication(pet_id); // 여기서 접근 가능
});
async function saveMedication(pet_id) {
  console.log(pet_id);
  const send_data = {
    pet_id: pet_id,
    medication_name: document.getElementById("medication_name_input").value,
    purpose: document.getElementById("purpose_input").value,
    dosage: document.getElementById("dosage_input").value,
    frequency: document.getElementById("frequency_option").value,
    start_date: document.getElementById("start_date_input").value,
    end_date: document.getElementById("end_date_input").value,
    side_effects_notes:
      document.getElementById("side_effects_notes_input").value || None,
    hospital_name: document.getElementById("hospital_name_input").value || None,
  };
  const response = await fetch(`/api/dailycares/save/medication/${pet_id}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(send_data),
  });

  if (!response.ok) {
    alert("기록저장이 실패되었습니다.");
  } else {
    console.log("기록저장완료");
  }
} // end saveMedication()
