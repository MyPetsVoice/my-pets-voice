import pytest
from unittest.mock import patch, MagicMock
from flask import Flask
import sys, os

# -----------------------------
# 경로 설정: 프로젝트 루트 포함
# -----------------------------
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.services.dailycare.care_chatbot_service import CareChatbotService

# -----------------------------
# 가짜 데이터
# -----------------------------
FAKE_PET = {
    "pet_name": "초코",
    "species_name": "강아지",
    "breed_name": "푸들",
    "pet_age": 3,
    "pet_gender": "여",
    "is_neutered": True,
}

FAKE_HEALTH_RECORDS = [
    MagicMock(weight_kg=5.2, food="3", water="300", excrement_status="정상", walk_time_minutes=30)
]

# -----------------------------
# Flask 앱 fixture
# -----------------------------
@pytest.fixture(scope="module")
def flask_app():
    app = Flask(__name__)
    app.config['TESTING'] = True
    with app.app_context():
        yield app

# -----------------------------
# 서비스 모킹
# -----------------------------
@pytest.fixture(autouse=True)
def mock_services(monkeypatch):
    # PetService / HealthCareService / MedicalCareService 모킹
    monkeypatch.setattr("app.services.pet.PetService.get_pet", lambda pet_id: FAKE_PET)
    monkeypatch.setattr("app.services.dailycare.healthcare_service.HealthCareService.get_health_records_by_pet", lambda pet_id: FAKE_HEALTH_RECORDS)
    monkeypatch.setattr("app.services.dailycare.medicalcare_service.MedicalCareService.get_allergy_pet", lambda pet_id: [])
    monkeypatch.setattr("app.services.dailycare.medicalcare_service.MedicalCareService.get_disease_pet", lambda pet_id: [])
    monkeypatch.setattr("app.services.dailycare.medicalcare_service.MedicalCareService.get_medications_by_pet", lambda pet_id: [])
    monkeypatch.setattr("app.services.dailycare.medicalcare_service.MedicalCareService.get_surgery_pet", lambda pet_id: [])
    monkeypatch.setattr("app.services.dailycare.medicalcare_service.MedicalCareService.get_vaccination_pet", lambda pet_id: [])

    # VectorStoreService 모킹
    mock_vector_store = MagicMock()
    mock_vector_store.store.similarity_search.return_value = [
        MagicMock(page_content="강아지 사료 급여 가이드", metadata={"source_file": "nutrition.pdf"})
    ]   #storage/documents/disease/brucella_dog.md
    monkeypatch.setattr("app.services.dailycare.vectorstore_service.VectorStoreService", lambda: mock_vector_store)

    # GPT 응답 모킹
    monkeypatch.setattr(
    "app.services.dailycare.care_chatbot_service.CareChatbotService.search_knowledge_base",
    lambda query, k=5: "브루셀라병은 강아지에게 위험할 수 있습니다."
)


# -----------------------------
# 실제 테스트
# -----------------------------
def test_chatbot_with_records(flask_app):
    # Flask 앱 컨텍스트 안에서 실행
    with flask_app.app_context():
        response = CareChatbotService.chatbot_with_records(
        user_input="강아지가 브루셀라병에 걸렸는지 의심되면 어떻게 해야 하나요?",
        pet_id=1,
        user_id=1,
        use_vector_search=True,
    )

        

        print("\n=== 챗봇 응답 ===\n", response)
        # 테스트 검증
        assert "강아지" in response
        assert "MOCK GPT RESPONSE" in response
