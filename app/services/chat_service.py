from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain.memory import ConversationBufferWindowMemory
from langchain.chains import LLMChain
from app.models.pet_persona import PetPersona


# ------------------------------
# 서비스 함수: pet_id로 persona 프롬프트 가져오기
# ------------------------------
class ChatService:
    @staticmethod
    def get_persona_prompt(pet_id: int):
        persona = PetPersona.find_by_pet_id(pet_id)
        if not persona:
            return None
        return persona  # PetPersona 인스턴스 반환

# ------------------------------
# LangChain 초기화
# ------------------------------
llm = ChatOpenAI(model='gpt-3.5-turbo')
memory = ConversationBufferWindowMemory(
    k=50,
    return_messages=True,
    memory_key='chat_history',
    input_key='user_input',
    output_key='ai_response'
)

# ------------------------------
# 시스템 프롬프트 생성
# ------------------------------
def get_system_prompt(pet_id: int):
    persona = ChatService.get_persona_prompt(pet_id)
    if not persona:
        return "등록된 페르소나가 없습니다."

    # Pet 모델 정보는 self.pet을 통해 접근
    pet = persona.pet

    system_prompt = f"""
너는 지금부터 사용자의 반려동물인 {pet.pet_name}로 대화한다.

[반려동물 정보]
- 종: {getattr(pet, 'species', '알 수 없음')} ({getattr(pet, 'breed', '알 수 없음')}, {getattr(pet, 'age', '알 수 없음')}살, {getattr(pet, 'gender', '알 수 없음')})
- 성격: {persona.personality_traits or '정보 없음'}
- 좋아하는 것: {persona.favorite_activities or '정보 없음'}
- 싫어하는 것: {persona.dislikes or '정보 없음'}
- 습관: {persona.habits or '정보 없음'}
- 주인과의 관계: {persona.user_nickname or '정보 없음'}
- 특이사항: {persona.special_note or '정보 없음'}
- 대화 스타일: {persona.speaking_style or '정보 없음'}

[대화 규칙]
- 반드시 반려동물로서 대화한다.
- 사람처럼 지식 전달을 하지 않는다.
- 주인의 말에 귀엽고 동물스러운 반응을 보인다.
"""
    return system_prompt

# ------------------------------
# 사용 예시
# ------------------------------
# prompt = get_system_prompt(pet_id=1)
# print(prompt)
