from dotenv import load_dotenv
from app.services.pet_service import PetService
from app.services.dailycare.healthcare_service import HealthCareService
from app.services.dailycare.medicalcare_service import MedicationService
from app.services.dailycare.openAI_service import get_gpt_response
from flask import current_app as app

load_dotenv()


class careChatbotService:
    # record_type 별 attribute 매핑
    ATTRIBUTE_MAP = {
        "health": {
            "weight_kg": ["몸무게", "체중"],
            "food": ["음식", "사료", "밥"],
            "water": ["물", "음수", '수분'],
            "excrement_status": ["배변", "변", '똥'],
            "walk_time": ["산책", "걷기", '산책시간'],
        },
        "allergy": {
            "allergen": ["알러지", "알레르기"],
            "reaction": ["반응", "증상"],
        },
        "disease": {
            "disease_name": ["질병", "병명"],
            "diagnosis_date": ["진단일", "발병일"],
        },
        "medication": {
            "medication_name": ["약", "약품", "투약"],
            "dosage": ["용량", "복용량"],
        },
        "surgery": {
            "surgery_type": ["수술", "수술종류"],
            'surgery_name': ['수술명'],
            "surgery_date": ["수술일", "수술날짜"],
            "hospital_name": ['병원명', '수술병원'],
            'recovery_status': ['회복상태', '현재회복상태'],
            "doctor_name": ['의사', '집도의']
        },
        "vaccination": {
            "vaccine_name": ["백신", "예방접종"],
            "vaccination_date": ["접종일", "맞은날"],
            "next_vaccination_date": ["다음 접종", "재접종"],
        },
    }

    # -----------------------------
    # 공통 함수
    # -----------------------------
    @staticmethod
    def get_pet_records(pet_id: int):
        """pet 및 관련 기록 조회"""
        return {
            'pet': PetService.get_pet(pet_id),
            'health': HealthCareService.get_health_records_by_pet(pet_id),
            'allergy': MedicationService.get_allergy_pet(pet_id),
            'disease': MedicationService.get_disease_pet(pet_id),
            'medication': MedicationService.get_medications_by_pet(pet_id),
            'surgery': MedicationService.get_surgery_pet(pet_id),
            'vaccination': MedicationService.get_vaccination_pet(pet_id),
        }

    @staticmethod
    def summarize_record_list(records, record_type: str, limit: int = 3) -> list:
        """ATTRIBUTE_MAP을 이용해 record 속성별 요약"""
        if not records:
            return []

        attr_map = careChatbotService.ATTRIBUTE_MAP.get(record_type, {})
        summaries = []
        for r in records[:limit]:  # 최근 limit개만 요약
            parts = []
            for attr in attr_map.keys():
                val = getattr(r, attr, None)
                if val:
                    parts.append(f"{attr}: {val}")
            summaries.append(" | ".join(parts))
        return summaries

    @staticmethod
    def summarize_pet_records(records: dict) -> str:
        """반려동물 기록 요약"""
        pet = records["pet"]
        print(pet)

        return f"""
        반려동물: {pet['pet_name']} ({pet['species_name']} - {pet['breed_name']})
        나이/성별: {pet['pet_age']}살, {pet['pet_gender']} / 중성화: {"O" if pet['is_neutered'] else "X"}
        
        최근 건강 기록: {careChatbotService.summarize_record_list(records['health'], 'health')}
        알러지: {careChatbotService.summarize_record_list(records['allergy'], 'allergy')}
        질병: {careChatbotService.summarize_record_list(records['disease'], 'disease')}
        복용 중인 약: {careChatbotService.summarize_record_list(records['medication'], 'medication')}
        수술 내역: {careChatbotService.summarize_record_list(records['surgery'], 'surgery')}
        예방접종 내역: {careChatbotService.summarize_record_list(records['vaccination'], 'vaccination')}
        """

    @staticmethod
    def build_prompt(user_input: str, records_summary: str) -> str:
        """GPT 프롬프트 구성"""
        return f"""
        너는 반려동물 건강 상담 챗봇이야.
        참고할 반려동물 기록은 아래와 같아:

        {records_summary}

        사용자의 질문: {user_input}
        """

    # -----------------------------
    # 챗봇 핵심 함수
    # -----------------------------
    @staticmethod
    def chatbot_with_records(user_input: str, pet_id: int, user_id: int) -> str:
        with app.app_context():
            records = careChatbotService.get_pet_records(pet_id)
            summary = careChatbotService.summarize_pet_records(records)

        prompt = careChatbotService.build_prompt(user_input, summary)
        prompt = careChatbotService.pretty_format(prompt)
        return get_gpt_response(prompt)
    
    
    @staticmethod
    def pretty_format(text: str) -> str:
        lines = text.split("\n")
        return "\n".join("  " + line.strip() for line in lines if line.strip())

