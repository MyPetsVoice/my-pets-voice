from dotenv import load_dotenv
from app import create_app
from app.services.pet_service import PetService
from app.services.dailycare.healthcare_service import HealthCareService
from app.services.dailycare.medicalcare_service import MedicationService
from app.services.dailycare.openAI_service import get_gpt_response

load_dotenv()

# Flask app 생성
app, db = create_app()

def get_pet_records(pet_id:int):
        """pet 정보 조회"""
        pet = PetService.get_pet(pet_id)
        return pet
    
class PetRecordsService:
    """반려동물 기록 관련 서비스 클래스"""
    
   
    
    @staticmethod
    def get_health_records(pet_id: int) -> str:
        """건강 기록 조회"""
        with app.app_context():
            pet = get_pet_records(pet_id)
            print(pet)
            records = HealthCareService.get_health_records_by_pet(pet_id)
            if not records:
                return "건강 기록이 없습니다."
        
            summary = "📋 최근 건강 기록:\n"
            for i, record in enumerate(records[:5], 1):  # 최근 5개만
                # 객체의 속성들을 직접 접근해서 보기 좋게 표시
                date = record.created_at.strftime("%Y-%m-%d %H:%M") if hasattr(record, 'created_at') else "날짜 없음"
                weight = getattr(record, 'weight_kg', '미기록')
                food = getattr(record, 'food', '미기록')
                water = getattr(record, 'water' , '미기록')
                excrement_status = getattr(record, 'excrement_status', '미기록')
                walk_time = getattr(record, 'walk_time', '미기록')
                
                
                
                
                summary += f"{i}. 날짜: {date}"
                if weight != '미기록':
                    summary += f" | 체중: {weight}kg"
                if date != '미기록':
                    summary += f' | 일정: {date}'
                if food != '미기록':
                    summary += f' | 음식(g): {food}(g)'
                if water != '미기록':
                    summary += f' | 물(ml) : {water}(ml)'
                if excrement_status != '미기록':
                    summary += f' | 배변상태 :  {excrement_status}'
                if walk_time != '미기록':
                    summary += f' | 산책시간(min) : {walk_time}분 '
                summary += "\n"
            
            return summary
    
    @staticmethod
    def get_allergy_records(pet_id: int) -> str:
        """알러지 기록 조회"""
        with app.app_context():
            pet = get_pet_records(pet_id)
            print(pet)
            records = MedicationService.get_allergy_pet(pet_id)
            if not records:
                return "알러지 기록이 없습니다."
            
            summary = "🚨 알러지 정보:\n"
            for i, record in enumerate(records, 1):
                allergen = getattr(record, 'allergen', '미기록')
                allergy_type = getattr(record, 'allergy_type', '미기록')
                symptoms = getattr(record, 'symptoms' , '미기록' )
                severity = getattr(record, 'severity', '미기록')
                
                date = record.created_at.strftime("%Y-%m-%d") if hasattr(record, 'created_at') else "날짜 없음"
                
                summary += f"{i}. {allergen}"
                if severity != '미기록':
                    summary += f" 심각도 | {severity}"
                if allergy_type != '미기록':
                    summary += f' 알러지타입 | {allergy_type}'
                if symptoms != '미기록':
                    summary += f' 증상 | {symptoms}'
                if allergen != '미기록':
                    summary += f' 알러지원 | {allergen}'

                summary += f" - {date}\n"
            
            return summary
    
    @staticmethod
    def get_disease_records(pet_id: int) -> str:
        """질병 기록 조회"""
        with app.app_context():
            pet = get_pet_records(pet_id)
            print(pet)
            records = MedicationService.get_disease_pet(pet_id)
            if not records:
                return "질병 기록이 없습니다."
            
            summary = "🏥 질병 내역:\n"
            for i, record in enumerate(records, 1):
                disease = getattr(record, 'disease_name', '미기록')
                symptoms = getattr(record, 'symptoms', '미기록')
                treatment_details = getattr(record, 'treatment_details', '미기록')
                hospital_name = getattr(record, 'hospital_name' , '미기록')
                doctor = getattr(record, 'doctor_name' , '미기록' )
                medical_cost = getattr(record, 'medical_cost', '미기록')
                diagnosis_date = getattr(record, 'diagnosis_date', '미기록')
                date = record.created_at.strftime("%Y-%m-%d") if hasattr(record, 'created_at') else "날짜 없음"
                
                summary += f"{i}. {disease}"
                if symptoms != '미기록':
                    summary += f" 상태 | {symptoms}"
                if treatment_details != '미기록':
                    summary += f' 치료내역 | {treatment_details}'
                if hospital_name != '미기록':
                    summary += f' 병원 | {hospital_name}'
                if doctor != '미기록' :
                    summary += f' 의사 | { doctor }'
                if medical_cost != '미기록' :
                    summary += f' 병원비 | { medical_cost }'
                if diagnosis_date != '미기록':
                    summary += f' 진단일 | { diagnosis_date }'
                
                summary += f" - {date}\n"
            
            return summary
    
    @staticmethod
    def get_medication_records(pet_id: int) -> str:
        """투약 기록 조회"""
        with app.app_context():
            pet = get_pet_records(pet_id)
            print(pet)
            records = MedicationService.get_medications_by_pet(pet_id)
            if not records:
                return "복용 중인 약이 없습니다."
            
            summary = "💊 복용 중인 약:\n"
            for i, record in enumerate(records, 1):
                medication = getattr(record, 'medication_name', '미기록')
                dosage = getattr(record, 'dosage', '미기록')
                frequency = getattr(record, 'frequency', '미기록')
                date = record.created_at.strftime("%Y-%m-%d") if hasattr(record, 'created_at') else "날짜 없음"
                
                summary += f"{i}. {medication}"
                if dosage != '미기록':
                    summary += f" - 용량: {dosage}"
                if frequency != '미기록':
                    summary += f" - 복용법: {frequency}"
                
                summary += f" (시작일: {date})\n"
            
            return summary
    
    @staticmethod
    def get_surgery_records(pet_id: int) -> str:
        """수술 기록 조회"""
        with app.app_context():
            pet = get_pet_records(pet_id)
            print(pet)
            records = MedicationService.get_surgery_pet(pet_id)
            if not records:
                return "수술 기록이 없습니다."
            summary = "💻 수술 내역:\n"
            for i, record in enumerate(records, 1):
                surgery_name = getattr(record, 'surgery_name', '미작성')
                surgery_date = getattr(record, 'surgery_date', '미작성')
                surgery_summary = getattr(record, 'surgery_summary', '미작성')
                hospital_name = getattr(record , 'hospital_name' , '미작성' )
                doctor_name = getattr(record , 'doctor_name', '미완성')
                recovery_status = getattr(record , 'recovery_status', '미완성')
                if surgery_name != '미작성':
                    summary += f' 수술명 | {surgery_name}'
                if surgery_date != '미작성' : 
                    summary += f' 수술일 | {surgery_date}'
                if surgery_summary != '미작성' : 
                    summary += f' 수술요약 | {surgery_summary}'
                if hospital_name != '미작성' :
                    summary += f' 병원명 | {hospital_name}'
                if doctor_name != '미작성':
                    summary += f' 집도의 | {doctor_name}'
                if recovery_status != '미작성' :
                    summary += f' 회복상태 | {recovery_status}'
                    
                summary += f"{i}. {surgery_name}"
              
            
            return f"🔪 수술 내역: {', '.join(surgery_name)}"
    
    @staticmethod
    def get_vaccination_records(pet_id: int) -> str:
        """예방접종 기록 조회"""
        with app.app_context():
            pet = get_pet_records(pet_id)
            print(pet)
            records = MedicationService.get_vaccination_pet(pet_id)
            if not records:
                return "예방접종 기록이 없습니다."
            summary = '💉 수술내역:\n'
            for i, record in enumerate(records, 1):
                vaccination = getattr(record, 'vaccine_name', '미작성')
                vaccination_date = getattr(record, 'vaccination_date', '미작성')
                side_effects = getattr(record, 'side_effects', '미작성')
                hospital_name = getattr(record, 'hospital_name', '미작성' )
                next_vaccination_date = getattr(record, 'next_vaccination_date', '미작성')
                manufacturer = getattr(record, 'manufacturer' , '미작성')
                lot_number = getattr(record, 'lot_number', '미작성')  
                if vaccination != '미완성':
                    summary += f' 백신명 | {vaccination}'
                if vaccination_date != '미완성':
                    summary += f' 접종일자 | {vaccination_date}'
                if side_effects != '미완성' :
                    summary += f' 부작용 | {side_effects}'
                if hospital_name != '미작성':
                    summary += f' 병원 이름 | {hospital_name}'
                if next_vaccination_date != '미작성':
                    summary += f' 다음 접종일 | {next_vaccination_date} '
                if manufacturer != '미작성':
                    summary += f' 제조회서 | {manufacturer}'
                if lot_number != '미작성':
                    summary += f' 로트번호 | {lot_number} '     
                summary += f"{i}. {vaccination}"
            return f"💉 예방접종 내역: {', '.join(vaccination)}"
    
    @staticmethod
    def get_all_records(pet_id: int) -> str:
        """모든 기록 종합 조회"""
        pet = get_pet_records(pet_id)
        print(pet)
        health = PetRecordsService.get_health_records(pet_id)
        allergy = PetRecordsService.get_allergy_records(pet_id)
        disease = PetRecordsService.get_disease_records(pet_id)
        medication = PetRecordsService.get_medication_records(pet_id)
        surgery = PetRecordsService.get_surgery_records(pet_id)
        vaccination = PetRecordsService.get_vaccination_records(pet_id)
        
        return f"""
        {health}
        {allergy}
        {disease}
        {medication}
        {surgery}
        {vaccination}
        """.strip()


def detect_record_type(user_input: str) -> str:
    """사용자 입력에서 원하는 기록 유형 감지"""
    keywords = {
        'health': ['건강', '컨디션', '상태', '몸무게', '체중'],
        'allergy': ['알러지', '알레르기', '음식', '식품'],
        'disease': ['질병', '병', '아픈', '진단'],
        'medication': ['약', '투약', '복용', '처방'],
        'surgery': ['수술', '시술', '마취'],
        'vaccination': ['백신', '예방접종', '접종'],
        'all': ['전체', '모든', '모두', '종합', '전부']
    }
    
    user_lower = user_input.lower()
    for record_type, words in keywords.items():
        if any(word in user_lower for word in words):
            return record_type
    
    return 'general'  # 일반 상담


def chatbot_with_records(user_input: str, pet_id: int, user_id: int) -> str:
    """반려동물 기록 기반 상담 챗봇"""
    
    # 기록 유형 감지
    record_type = detect_record_type(user_input)
    
    # 요청된 기록만 조회
    if record_type == 'health':
        records_summary = PetRecordsService.get_health_records(pet_id)
    elif record_type == 'allergy':
        records_summary = PetRecordsService.get_allergy_records(pet_id)
    elif record_type == 'disease':
        records_summary = PetRecordsService.get_disease_records(pet_id)
    elif record_type == 'medication':
        records_summary = PetRecordsService.get_medication_records(pet_id)
    elif record_type == 'surgery':
        records_summary = PetRecordsService.get_surgery_records(pet_id)
    elif record_type == 'vaccination':
        records_summary = PetRecordsService.get_vaccination_records(pet_id)
    elif record_type == 'all':
        records_summary = PetRecordsService.get_all_records(pet_id)
    else:
        # 일반 상담인 경우 필요한 기본 정보만
        with app.app_context():
            health_records = HealthCareService.get_health_records_by_pet(pet_id)
            allergy_records = MedicationService.get_allergy_pet(pet_id)
            
            records_summary = f"""
최근 건강상태: {health_records[0] if health_records else '기록 없음'}
알러지: {[a.allergen for a in allergy_records] if allergy_records else '없음'}
            """.strip()
    
    # 특정 기록 요청인 경우 바로 반환
    if record_type in ['health', 'allergy', 'disease', 'medication', 'surgery', 'vaccination', 'all']:
        return records_summary
    
    # 일반 상담인 경우 GPT 응답
    prompt = f"""
너는 반려동물 건강 상담 챗봇이야.
참고할 반려동물 기록은 아래와 같아:

{records_summary}

사용자의 질문: {user_input}

기록을 참고해서 도움이 되는 답변을 해줘.
"""
    
    return get_gpt_response(prompt)


def show_menu():
    """메뉴 출력"""
    print("\n" + "="*50)
    print("🐾 반려동물 건강 상담 챗봇")
    print("="*50)
    print("명령어:")
    print("- '건강기록' : 건강 기록 조회")
    print("- '알러지' : 알러지 정보 조회") 
    print("- '질병' : 질병 내역 조회")
    print("- '약' : 복용 중인 약 조회")
    print("- '수술' : 수술 내역 조회")
    print("- '예방접종' : 백신 접종 내역 조회")
    print("- '전체기록' : 모든 기록 조회")
    print("- 'quit' 또는 'exit' : 종료")
    print("="*50)


def main():
    pet_id = 1   # 임시 테스트용
    user_id = 1  # 임시 테스트용
    
    show_menu()
    
    while True:
        user_input = input("\n💬 You: ")
        
        if user_input.lower() in ["quit", "exit"]:
            print("👋 안녕히 가세요!")
            break
            
        if user_input.lower() == "menu":
            show_menu()
            continue
        
        try:
            answer = chatbot_with_records(user_input, pet_id, user_id)
            print("🤖 Bot:", answer)
        except Exception as e:
            print(f"❌ 오류가 발생했습니다: {e}")


if __name__ == "__main__":
    main()