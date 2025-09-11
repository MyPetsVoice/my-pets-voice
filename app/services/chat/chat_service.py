from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_community.chat_message_histories import ChatMessageHistory
from app.models import Pet, PetPersona
from datetime import datetime
import logging
import os
from config import Config

logger = logging.getLogger(__name__)

# LangSmith 설정
if Config.LANGCHAIN_API_KEY:
    os.environ["LANGCHAIN_TRACING_V2"] = "true" if Config.LANGSMITH_TRACING else "false"
    os.environ["LANGCHAIN_API_KEY"] = Config.LANGCHAIN_API_KEY
    if Config.LANGSMITH_PROJECT:
        os.environ["LANGCHAIN_PROJECT"] = Config.LANGSMITH_PROJECT
    os.environ["LANGCHAIN_ENDPOINT"] = Config.LANGSMITH_ENDPOINT

class ChatService:
    def __init__(self):
        self.llm = ChatOpenAI(
            model='gpt-4o-mini',
            max_tokens=256,
            temperature=0.9,
            api_key=Config.OPENAI_API_KEY
        )
        
        # LCEL에서는 ChatMessageHistory 사용
        self.message_histories = {}  # 세션별 메시지 히스토리 저장

    # 0. 사용자의 펫 목록을 가져옴.
    def get_user_pets(self, user_id):
        try:
            pets_list = Pet.find_pets_by_user_id(user_id)
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
            'day_of_weekday': ['월', '화', '수', '목', '금', '토', '일'][now.weekday()],
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
        personality = ','.join([trait['trait_name'] for trait in pet_info.get('traits', [])])
        politeness = '반말' if pet_info.get('politeness') == 'informal' else '존댓말'
        speech_style = pet_info.get('style_name', '다정한 말투')
        likes = pet_info.get('likes', '')
        dislikes = pet_info.get('dislikes', '')
        habits = pet_info.get('habits', '')
        special_notes = pet_info.get('special_note', '')

        prompt = f"""당신은 사용자의 반려동물 {species} '{name}'(이)가 되어 사용자와 대화한다.
사용자를 '{user_call}'라고 부르며, '{politeness}' 말투와 '{speech_style}'로 항상 반려동물의 관점에서 대화한다.

[기본 정보]
- 품종: {breed}
- 나이: {age}살
- 성별: {gender}
- 생일: {pet_info.get('birthdate', '')}
- 입양일: {pet_info.get('adoption_date', '')}
- 성격: {personality}
- 말투: {speech_style}

[현재 상황]
- 오늘: {context['date']} {context['day_of_weekday']}요일
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
6. 사람처럼 지식을 전달하지 말고, 동물스러운 반응을 보이세요"""

        return prompt

    # 세션별 메시지 히스토리 관리 (LCEL 방식)
    def get_or_create_message_history(self, session_key):
        """세션별 ChatMessageHistory 생성 또는 반환"""
        if session_key not in self.message_histories:
            self.message_histories[session_key] = ChatMessageHistory()
        return self.message_histories[session_key]

    # 채팅 세션 생성
    def create_chat_session(self, session_key, pet_info):
        """새로운 채팅 세션을 생성하고 메시지 히스토리 초기화"""
        try:
            # 기존 세션이 있으면 정리
            if session_key in self.message_histories:
                self.message_histories[session_key].clear()
            
            # 새로운 메시지 히스토리 생성
            message_history = self.get_or_create_message_history(session_key)
            
            logger.info(f'채팅 세션 생성 완료 - Session: {session_key}, Pet: {pet_info.get("name", "Unknown")}')
            return True
            
        except Exception as e:
            logger.error(f'채팅 세션 생성 중 오류: {str(e)}')
            return False
    
    # 채팅 세션 삭제
    def delete_chat_session(self, session_key):
        """채팅 세션 삭제"""
        try:
            if session_key in self.message_histories:
                del self.message_histories[session_key]
                logger.info(f'채팅 세션 삭제 완료 - Session: {session_key}')
                return True
            return False
        except Exception as e:
            logger.error(f'채팅 세션 삭제 중 오류: {str(e)}')
            return False
    
    # 채팅 세션 조회
    def get_chat_session(self, session_key):
        """채팅 세션 존재 여부 확인"""
        return session_key in self.message_histories
    
    # 채팅 기록 초기화
    def reset_chat_history(self, session_key):
        """특정 세션의 채팅 기록만 초기화 (세션은 유지)"""
        try:
            if session_key in self.message_histories:
                self.message_histories[session_key].clear()
                logger.info(f'채팅 기록 초기화 완료 - Session: {session_key}')
                return True
            return False
        except Exception as e:
            logger.error(f'채팅 기록 초기화 중 오류: {str(e)}')
            return False

    # 메인 채팅 함수 (LCEL 방식)
    def chat(self, pet_info, user_input, session_key):
        logger.debug(f'입력된 펫 정보 : {pet_info}')
        try:
            system_prompt = self.create_system_prompt(pet_info)
            
            # ChatPromptTemplate with MessagesPlaceholder 사용
            prompt = ChatPromptTemplate.from_messages([
                ("system", system_prompt),
                MessagesPlaceholder(variable_name="chat_history"),
                ("human", "{input}")
            ])
            
            # LCEL 체인 구성
            chain = prompt | self.llm | StrOutputParser()
            
            # RunnableWithMessageHistory로 메모리 관리
            chain_with_history = RunnableWithMessageHistory(
                chain,
                self.get_or_create_message_history,
                input_messages_key="input",
                history_messages_key="chat_history",
            )
            
            # 응답 생성
            response = chain_with_history.invoke(
                {"input": user_input},
                config={"configurable": {"session_id": session_key}}
            )

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
        if session_key in self.message_histories:
            self.message_histories[session_key].clear()
            logger.info(f'메모리 초기화 완료 - Session: {session_key}')

    # 특정 세션의 메모리 조회
    def get_chat_history(self, session_key):
        if session_key in self.message_histories:
            return self.message_histories[session_key].messages
        return []


chat_service = ChatService()