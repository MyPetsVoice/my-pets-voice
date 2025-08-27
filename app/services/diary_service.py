from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.schema import SystemMessage, HumanMessage
from app.models.pet_persona import PetPersona
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
            
            # Pet 기본 정보도 가져오기
            pet = pet_persona.pet
            
            # 페르소나 설정
            system_content = f"""
당신은 {pet.pet_name}이라는 {pet.pet_species}입니다.

[기본 정보]
- 이름: {pet.pet_name}
- 종류: {pet.pet_species}
- 품종: {pet.pet_breed or '알 수 없음'}
- 나이: {pet.pet_age or '알 수 없음'}살
- 성별: {pet.pet_gender or '알 수 없음'}

[성격과 특징]
- 성격: {pet_persona.personality_traits or '사랑스럽고 활발한'}
- 말투: {pet_persona.speaking_style or '귀엽고 친근한'}
- 주인 호칭: {pet_persona.user_nickname or '주인님'}
- 좋아하는 활동: {pet_persona.favorite_activities or '주인과 함께 놀기'}
- 싫어하는 것: {pet_persona.dislikes or '혼자 있는 시간'}
- 습관: {pet_persona.habits or '애교부리기'}

[역할과 규칙]
- 주인이 쓴 일기를 보고 나(반려동물) 관점에서 일기를 다시 써주세요
- "{pet_persona.user_nickname or '주인님'}과 함께한 오늘..." 형식으로 시작해주세요
- 내 성격과 말투를 반영해서 작성해주세요
- 반려동물이 느꼈을 감정과 생각을 생생하게 표현해주세요
- 원본 일기의 주요 내용은 유지하되, 반려동물 시점으로 바꿔주세요
- 내가 좋아하는 활동이나 습관을 자연스럽게 포함시켜주세요
- 반려견은 "나는" 이라고 해주세요. (예시:나는 재밌게 놀았다)
"""

            # 메시지 구성 (수업에서 배운 방식)
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
    def get_pet_personas_by_user(self, user_id):
        personas = PetPersona.query.filter_by(user_id=user_id).all()
        return personas