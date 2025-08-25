from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain.memory import ConversationBufferWindowMemory
from langchain.chains import LLMChain
from app.models import Pet, PetPersona, PersonaTrait
from dotenv import load_dotenv

load_dotenv()

pet_profile = PetPersona.get_persona_prompt() # 클래스메서드 아니고 인스턴스 메서드라서 인스턴스 생성먼저 해야함.

llm = ChatOpenAI(model='gpt-4o')

memory = ConversationBufferWindowMemory(k=50, return_messages=True, memory_key='chat_history', input_key='user_input', output_key='ai_response')


# 0. 사용자의 펫 목록을 가져옴.
pets_list = Pet.get_pets_by_user_id('user_id')
print(f'사용자의 펫 목록 : {pets_list}')

def get_system_prompt(pet_id):
    # 프롬프트에 날짜, 시간, 날씨 넣기

    # 1. 선택된 펫의 정보를 가져옴.( 이름, 종류, 품종, 나이, 생일 등 걍 다 가져와....)
    pet_info = Pet.get_pet_by_pet_id(pet_id)
    print(f'선택된 반려동물의 기본 정보 : {pet_info}')

    # 2. 페르소나 정보를 가져옴.( 사용자 호칭, 말투, 성격 및 특징, 그 외 기타 사항)
    persona_info = [persona.to_dict() for persona in PetPersona.find_by_pet_id('pet_id')]
    persona_id = persona_info.pet_persona_id
    persona_traits = PersonaTrait.find_by_persona_id(persona_id)
    print(f'선택된 반려동물의 페르소나 정보 : {persona_info}')
    print(f'선택된 반려동물의 페르소나 성격 및 특징 : {persona_traits}')

    system_prompt = f"""
    너는 지금부터 사용자의 반려동물인 {pet_profile['species']} '{pet_profile['name']}'로 대화한다.

    [반려동물 정보]
    - 종: {pet_profile['species']} ({pet_profile['breed']}, {pet_profile['age']}살, {pet_profile['gender']})
    - 외형: {pet_profile['appearance']['color']}, {', '.join(pet_profile['appearance']['features'])}
    - 성격: {', '.join(pet_profile['personality']['traits'])}
    - 좋아하는 것: {', '.join(pet_profile['personality']['likes'])}
    - 싫어하는 것: {', '.join(pet_profile['personality']['dislikes'])}
    - 주인과의 관계: {pet_profile['relationship']['with_owner']}
    - 다른 존재와의 관계: {pet_profile['relationship']['with_others']}
    - 대화 스타일: {pet_profile['dialogue_style']['tone']}
    - 대표 표현: {', '.join(pet_profile['dialogue_style']['expressions'])}
    - 습관: {', '.join(pet_profile['dialogue_style']['habits'])}

    [대화 규칙]
    - 반드시 반려동물로서 대화한다.
    - 사람처럼 지식 전달을 하지 않는다.
    - 주인의 말에 귀엽고 동물스러운 반응을 보인다.
    # - 감정을 묘사할 때 동물 특유의 행동(꼬리 흔들기, 골골거리기 등)을 포함한다.
    """
    return system_prompt



