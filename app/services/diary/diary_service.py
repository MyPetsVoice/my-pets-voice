from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
from app.models.pet_persona import PetPersona
from app.models.diary import Diary, DiaryPhoto
import os

class DiaryService:
    def __init__(self):
        load_dotenv()
        self.llm = ChatOpenAI(
            model="gpt-3.5-turbo",
            temperature=0.7,
            max_tokens=1000,
            api_key=os.getenv("OPENAI_API_KEY")
        )
    
    def convert_to_pet_diary(self, user_content, pet_persona_id):
        # 사용자 일기를 반려동물 관점으로 변환
        try:
            # PetPersona 정보 가져오기
            pet_persona = PetPersona.query.get(pet_persona_id)
            if not pet_persona:
                raise ValueError("반려동물 페르소나 정보를 찾을 수 없습니다.")
            
            #펫 기본정보.
            pet = pet_persona.pet
            
            species_name = pet.species.species_name if pet.species else '반려동물'
            breed_name = pet.breeds.breed_name if pet.breeds else '알 수 없음'
            
            # 페르소나 설정
            system_content = f"""
당신은 {pet.pet_name}이라는 {species_name}입니다.

[기본 정보]
- 이름: {pet.pet_name}
- 종류: {species_name}
- 품종: {breed_name}
- 나이: {pet.pet_age}살
- 성별: {pet.pet_gender}

[성격과 특징]
- 말투: {pet_persona.speech_habit}
- 주인 호칭: {pet_persona.user_call}
- 좋아하는 것: {pet_persona.likes}
- 싫어하는 것: {pet_persona.dislikes}
- 습관: {pet_persona.habits}
- 가족 정보: {pet_persona.family_info or ''}
- 특별한 점: {pet_persona.special_note or ''}

[역할과 규칙]
- 주인이 쓴 일기를 보고 나(반려동물) 관점에서 일기를 다시 써주세요
- "{pet_persona.user_call or '주인님'}과 함께한 오늘..." 형식으로 시작해주세요
- 내 성격과 말투를 반영해서 작성해주세요
- 반려동물이 느꼈을 감정과 생각을 생생하게 표현해주세요
- 원본 일기의 주요 내용은 유지하되, 반려동물 시점으로 바꿔주세요
- 내가 좋아하는 것이나 습관을 자연스럽게 포함시켜주세요
- 반려동물은 "나는" 이라고 해주세요. (예시:나는 재밌게 놀았다)
"""

            # 메시지 구성
            messages = [
                SystemMessage(content=system_content),
                HumanMessage(content=f"주인이 쓴 일기입니다. 이를 {pet.pet_name}의 관점에서 다시 써주세요:\n\n{user_content}")
            ]
            
            # AI 호출
            result = self.llm.invoke(messages)
            return result.content
            
        except Exception as e:
            print(f"AI 변환 오류: {str(e)}")
            raise Exception(f"AI 변환 중 오류가 발생했습니다: {str(e)}")

    # 페르소나 가져오기
    @staticmethod
    def get_pet_personas_by_user(user_id):
        personas = PetPersona.query.filter_by(user_id=user_id).all()
        return personas
    
    @staticmethod
    def get_all_diaries(user_id):
        """전체 일기 목록 (최신순)"""
        return Diary.query.filter_by(user_id=user_id).order_by(Diary.diary_date.desc()).all()
    
    @staticmethod
    def get_by_pet_persona(pet_persona_id):
        """특정 펫 페르소나의 일기 목록"""
        return Diary.query.filter_by(pet_persona_id=pet_persona_id).order_by(Diary.diary_date.desc()).all()
    
    @staticmethod
    def get_by_user(user_id):
        """특정 사용자의 모든 일기"""
        return Diary.query.filter_by(user_id=user_id).order_by(Diary.diary_date.desc()).all()
    
    @staticmethod
    def get_by_date_range(start_date, end_date):
        """날짜 범위로 일기 조회"""
        return Diary.query.filter(Diary.diary_date.between(start_date, end_date)).order_by(Diary.diary_date.desc()).all()
    
    @staticmethod
    def get_recent_diaries(limit=10):
        """최근 일기 목록"""
        return Diary.query.order_by(Diary.diary_date.desc()).limit(limit).all()
    
    @staticmethod
    def search_by_title(search_term):
        """제목으로 일기 검색"""
        return Diary.query.filter(Diary.title.contains(search_term)).order_by(Diary.diary_date.desc()).all()
    
    @staticmethod
    def get_photos_by_diary(diary_id):
        """특정 일기의 모든 사진"""
        return DiaryPhoto.query.filter_by(diary_id=diary_id).order_by(DiaryPhoto.display_order).all()