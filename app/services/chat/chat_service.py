from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain.schema import SystemMessage, HumanMessage, AIMessage
from langchain.memory import ConversationBufferWindowMemory
from langchain.chains import LLMChain
from app.models import Pet, PetPersona, PersonaTrait
from dotenv import load_dotenv
from datetime import datetime
import logging

load_dotenv()
logger = logging.getLogger(__name__)


class ChatService:
    def __init__(self):
        self.llm = ChatOpenAI(
            model='gpt-4o-mini',
            max_tokens=256,
            temperature=0.8
        )

        self.memories = {} # 사용자별 메모리 관리를 위한 딕셔너리

    # 0. 사용자의 펫 목록을 가져옴.
    def get_user_pets(self, user_id):
        try:
            pets_list = Pet.find_pets_by_user_id(user_id) # to_dict 해야하는데... 걍. 아예 모델의 메서드에서 다 to_dict 해서 반환하도록 변경하는게 나을 듯.
            return pets_list
        
        except Exception as e:
            logger.error(f'펫 목록 조회 중 오류 {str(e)}')
            return []

    # 1. 선택된 펫의 정보를 통합(기본 정보+페르소나 정보)
    def get_pet_info(self, pet_id):
        # 1-1. 선택된 펫의 정보를 가져옴.( 이름, 종류, 품종, 나이, 생일 등 걍 다 가져와....)
        pet_info = Pet.find_pet_by_pet_id(pet_id)
        logger.debug(f'선택된 반려동물의 기본 정보 : {pet_info}')

        # 1-2. 페르소나 정보를 가져옴.( 사용자 호칭, 말투, 성격 및 특징, 그 외 기타 사항)
        persona_info = PetPersona.get_persona_info(pet_id)
        logger.debug(f'선택된 반려동물의 페르소나 정보 : {persona_info}')

        return pet_info

    # 2. 날짜나 시간 정보 가져오기
    def get_current_context(self):
        now = datetime.now()

        weather = '맑음' # 날씨 api 가져와서 적용하는 것으로 수정

        context = {
            'date': now.strftime('%Y년 %m월 %d일'),
            'time': now.strftime('%H시 %M분'),
            'day of weekday': ['월', '화', '수', '목', '금', '토', '일'][now.weekday()],
            'weather': weather
        }
        return context

    # 3. 시스템 프롬프트 생성
    def create_system_prompt(self, pet_info):
        """펫 정보를 바탕으로 시스템 프롬프트 생성"""
        context = self.get_current_context()
        
        # 기본 정보 구성 (세션 데이터 구조에 맞춤)
        name = pet_info.get('pet_name', '')
        species = pet_info.get('species_name', '') 
        breed = pet_info.get('breed_name')
        age = pet_info.get('pet_age')  
        gender = pet_info.get('pet_gender')  
        user_call = pet_info.get('user_call', '')
        
        # 성격 및 특성 (세션 데이터 구조에 맞춤)
        personality = ','.join([trait['trait_name'] for trait in pet_info.get('traits')])
        politeness =  '반말' if pet_info.get('politeness') == 'informal' else '존댓말'
        speech_style = pet_info.get('style_name', '다정한 말투')
        likes = pet_info.get('likes', '')
        dislikes = pet_info.get('dislikes', '')
        habits = pet_info.get('habits', '')
        special_notes = pet_info.get('special_note', '')

        prompt = f"""
            당신은 사용자의 반려동물 {species} '{name}'(이)가 되어 사용자와 대화한다.
            사용자를 '{user_call}'라고 부르며, '{politeness}' 말투와 '{speech_style}'로 항상 반려동물의 관점에서 대화한다.

            [기본 정보]
            - 품종: {breed}
            - 나이: {age}살
            - 성별: {gender}
            - 생일: {pet_info.get('birthdate')}
            - 입양일: {pet_info.get('adoption_date')}
            - 성격: {personality}
            - 말투: {speech_style}

            [현재 상황]
            - 오늘: {context['date']} {context['day of weekday']}요일
            - 시간: {context['time']}
            - 날씨: {context['weather']}


            [추가 정보]"""

        if likes:
            prompt += f"\n- 좋아하는 것: {likes}"
        if dislikes:
            prompt += f"\n- 싫어하는 것: {dislikes}"
        if habits:
            prompt += f"\n- 습관: {habits}"
        if special_notes:
            prompt += f"\n- 특이사항: {special_notes}"

        prompt += f"""

            [대화 규칙]
            1. {speech_style}로 일관되게 대화하세요
            2. {name}의 성격({personality})을 잘 표현하세요
            3. 반려동물 관점에서 자연스럽게 대화하세요
            4. 한국어로 대답하세요
            5. 답변은 길지 않고 단순하게 1-2문장으로 대화한다.
            6. 사람처럼 지식을 전달하지 말고, 동물스러운 반응을 보이세요
            """

        return prompt


    # 세션별 메모리 관리
    def get_or_create_memory(self, session_key):
        if session_key not in self.memories:
            self.memories[session_key] = ConversationBufferWindowMemory(
                k=20,
                return_messages=True,
                memory_key='chat_history'
            )
        # memory = ConversationBufferWindowMemory(k=50, return_messages=True, memory_key='chat_history', input_key='user_input', output_key='ai_response')
        return self.memories[session_key]

    # 채팅 세션 생성
    def create_chat_session(self, session_key, pet_info):
        """새로운 채팅 세션을 생성하고 메모리 초기화"""
        try:
            # 기존 세션이 있으면 정리
            if session_key in self.memories:
                self.memories[session_key].clear()
            
            # 새로운 메모리 생성
            memory = self.get_or_create_memory(session_key)
            
            logger.info(f'채팅 세션 생성 완료 - Session: {session_key}, Pet: {pet_info.get("name", "Unknown")}')
            return True
            
        except Exception as e:
            logger.error(f'채팅 세션 생성 중 오류: {str(e)}')
            return False
    
    # 채팅 세션 삭제
    def delete_chat_session(self, session_key):
        """채팅 세션 삭제"""
        try:
            if session_key in self.memories:
                del self.memories[session_key]
                logger.info(f'채팅 세션 삭제 완료 - Session: {session_key}')
                return True
            return False
        except Exception as e:
            logger.error(f'채팅 세션 삭제 중 오류: {str(e)}')
            return False
    
    # 채팅 세션 조회
    def get_chat_session(self, session_key):
        """채팅 세션 존재 여부 확인"""
        return session_key in self.memories
    
    # 채팅 기록 초기화
    def reset_chat_history(self, session_key):
        """특정 세션의 채팅 기록만 초기화 (세션은 유지)"""
        try:
            if session_key in self.memories:
                self.memories[session_key].clear()
                logger.info(f'채팅 기록 초기화 완료 - Session: {session_key}')
                return True
            return False
        except Exception as e:
            logger.error(f'채팅 기록 초기화 중 오류: {str(e)}')
            return False
        


    # 메인 채팅 함수
    def chat(self, pet_info, user_input, session_key):
        logger.debug(f'입력된 펫 정보 : {pet_info}')
        try:
            system_prompt = self.create_system_prompt(pet_info)

            memory = self.memories[session_key]

            prompt_template = ChatPromptTemplate.from_messages([
                ('system', system_prompt),
                ('human', '{user_input}')
            ])

            chain = LLMChain(llm=self.llm, prompt=prompt_template, memory=memory, verbose=True)

            response = chain.predict(user_input=user_input)

            logger.info(f'채팅 응답 생성 완료 - Pet: {pet_info.get("pet_name", "Unknown")}, Response length: {len(response)}')

            return {
                'success': True,
                'response': response,
                'pet_name': pet_info.get('pet_name', 'Pet')
            }

        except Exception as e:
            logger.error(f'채팅 처리 중 오류 ; {str(e)}')
            return {
                'success': False,
                'error': str(e),
                'response': '죄송해요, 지금은 대답하기 어려워요...ㅠㅠ'
            }
        
    # 특정 세션의 메모리 초기화
    def clear_memory(self, session_key):
        if session_key in self.memories:
            self.memories[session_key].clear()
            logger.info(f'메모리 초기화 완료 - Session: {session_key}')

    # 특정 세션의 메모리 조회
    def get_chat_history(self, session_key):
        if session_key in self.memories:
            return self.memories[session_key].chat_memory.messages
        return []


chat_service = ChatService()