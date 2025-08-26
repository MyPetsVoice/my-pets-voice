from flask import Blueprint, request, jsonify, session, current_app
from flask_socketio import SocketIO, emit, join_room, leave_room
from langchain_openai import ChatOpenAI
from langchain.schema import SystemMessage, HumanMessage, AIMessage
from app.models.pet_persona import PetPersona, PersonaTrait, SpeechStyle
from app.models.pet import Pet
import os
import json
import threading
import time
import logging

logger = logging.getLogger(__name__)

chat_api_bp = Blueprint('chat_api', __name__)

socketio = None  # 메인 앱에서 초기화됨
llm = None  # LangChain ChatOpenAI 모델 (앱 컨텍스트에서 초기화)

# 채팅 세션 저장 딕셔너리
chat_sessions = {}

# 1. 사용자의 반려동물 정보 가져오기(페르소나 없으면 목록에 안 뜨게)
# 2. 반려동물 선택하면 해당 페르소나 정보 가져오기(프로필 아래 출력) 
#       그런데 이제 펫의 기본 정보와 페르소나 정보를 모두 가져와야 하는.
# 3.

def init_socketio(app_socketio, app):
    """메인 앱에서 SocketIO 객체와 Flask 앱을 전달받아 초기화"""
    global socketio, llm
    socketio = app_socketio
    
    # config에서 OpenAI API 키 가져오기
    openai_api_key = app.config.get('OPENAI_API_KEY')
    if not openai_api_key:
        logger.error("OPENAI_API_KEY가 설정되지 않았습니다.")
        raise ValueError("OPENAI_API_KEY 환경변수가 설정되지 않았습니다.")
    
    llm = ChatOpenAI(
        api_key=openai_api_key,
        model="gpt-4o-mini",
        temperature=0.8,
        max_tokens=500
    )
    logger.info("ChatOpenAI 모델이 초기화되었습니다.")
    
    # SocketIO 이벤트 핸들러들 등록
    @socketio.on('connect')
    def on_connect():
        logger.info(f"클라이언트 연결됨: {request.sid}")
        
        # 채팅 세션 초기화 (펫 정보가 없어도 세션 생성)
        chat_sessions[request.sid] = {
            'pet_info': session.get('pet_info', None),
            'messages': [],
            'created_at': time.time()
        }
        
        join_room(request.sid)
        
        # 펫 정보가 있으면 로드 완료 로그
        if 'pet_info' in session:
            pet_name = session['pet_info'].get('name', '알 수 없음')
            logger.info(f"펫 정보 로드됨: {pet_name} (세션: {request.sid})")
        else:
            logger.info(f"펫 정보 대기 중 (세션: {request.sid})")

    @socketio.on('disconnect')  
    def on_disconnect():
        logger.info(f"클라이언트 연결 종료: {request.sid}")
        if request.sid in chat_sessions:
            del chat_sessions[request.sid]
            logger.debug(f"채팅 세션 삭제됨: {request.sid}")
        leave_room(request.sid)

    @socketio.on('send_message')
    def handle_message(data):
        try:
            # 입력값 검증
            if not data or 'message' not in data:
                logger.warning(f"잘못된 메시지 형식: {data}")
                emit('error', {'message': '메시지 형식이 올바르지 않습니다.'})
                return
            
            user_message = data['message'].strip()
            if not user_message:
                emit('error', {'message': '빈 메시지는 보낼 수 없습니다.'})
                return
            
            if len(user_message) > 1000:  # 메시지 길이 제한
                emit('error', {'message': '메시지가 너무 깁니다. (최대 1000자)'})
                return
            
            client_sid = request.sid
            
            if client_sid not in chat_sessions:
                logger.error(f"존재하지 않는 채팅 세션: {client_sid}")
                emit('error', {'message': '채팅 세션이 존재하지 않습니다.'})
                return
                
            chat_session = chat_sessions[client_sid]
            pet_info = chat_session['pet_info']
            
            # 펫 정보가 설정되지 않은 경우
            if not pet_info:
                emit('error', {'message': '반려동물을 먼저 선택해주세요.'})
                return
            
            logger.debug(f"메시지 수신 - 사용자: {user_message[:50]}...")
            
            # 사용자 메시지 저장 및 브로드캐스트
            chat_session['messages'].append({'role': 'user', 'content': user_message})
            emit('user_message', {'message': user_message})
            
            # 타이핑 인디케이터 표시
            emit('bot_typing', {'pet_name': pet_info['name']})
        
            # 백그라운드에서 AI 응답 생성
            def generate_response():
                try:
                    if llm is None:
                        logger.error("ChatOpenAI 모델이 초기화되지 않았습니다.")
                        socketio.emit('error', {
                            'message': '서비스가 준비되지 않았습니다. 잠시 후 다시 시도해주세요.'
                        }, room=client_sid)
                        return
                    
                    # 펫 페르소나 정보로 시스템 프롬프트 생성
                    system_prompt = create_pet_system_prompt(pet_info)
                    
                    # 대화 히스토리 구성
                    messages = [SystemMessage(content=system_prompt)]
                    
                    # 최근 10개 메시지만 포함
                    recent_messages = chat_session['messages'][-10:]
                    for msg in recent_messages:
                        if msg['role'] == 'user':
                            messages.append(HumanMessage(content=msg['content']))
                        else:
                            messages.append(AIMessage(content=msg['content']))
                    
                    logger.debug(f"AI 응답 생성 시작 - 펫: {pet_info.get('name', '알 수 없음')}")
                    
                    # AI 응답 생성
                    response = llm.invoke(messages)
                    bot_message = response.content
                    
                    if not bot_message:
                        logger.warning("AI 응답이 비어있습니다.")
                        bot_message = "죄송해요, 지금은 말하기 어려워요... 🥺"
                    
                    # 응답 저장
                    chat_session['messages'].append({'role': 'assistant', 'content': bot_message})
                    
                    # 클라이언트에게 응답 전송
                    socketio.emit('bot_response', {
                        'message': bot_message,
                        'pet_name': pet_info.get('name', '펫')
                    }, room=client_sid)
                    
                    logger.debug(f"AI 응답 완료 - 길이: {len(bot_message)}자")
                    
                except Exception as e:
                    logger.error(f"AI 응답 생성 중 오류: {str(e)}")
                    socketio.emit('error', {
                        'message': '죄송해요, 지금은 대답하기 어려워요... 😔'
                    }, room=client_sid)
            
            # 별도 스레드에서 응답 생성
            threading.Thread(target=generate_response, daemon=True).start()
            
        except Exception as e:
            logger.error(f"메시지 처리 중 오류: {str(e)}")
            emit('error', {'message': '메시지 처리 중 오류가 발생했습니다.'})

    @socketio.on('reset_chat')
    def handle_reset():
        try:
            if request.sid in chat_sessions:
                chat_sessions[request.sid]['messages'] = []
                logger.info(f"채팅 초기화: {request.sid}")
                emit('chat_reset', {'message': '대화가 초기화되었습니다.'})
            else:
                emit('error', {'message': '채팅 세션을 찾을 수 없습니다.'})
        except Exception as e:
            logger.error(f"채팅 초기화 중 오류: {str(e)}")
            emit('error', {'message': '채팅 초기화 중 오류가 발생했습니다.'})

def create_pet_system_prompt(pet_info):
    """펫 정보를 바탕으로 시스템 프롬프트 생성"""
    name = pet_info['name']
    species = pet_info['species']
    breed = pet_info['breed'] 
    age = pet_info['age']
    gender = pet_info['gender']
    owner_call = pet_info['owner_call']
    personality = ', '.join(pet_info['personality']) if pet_info['personality'] else '귀여운'
    speech_style = pet_info['speech_style']
    likes = ', '.join(pet_info['likes']) if pet_info['likes'] else ''
    dislikes = ', '.join(pet_info['dislikes']) if pet_info['dislikes'] else ''
    habits = ', '.join(pet_info['habits']) if pet_info['habits'] else ''
    special_notes = pet_info['special_notes']
    
    prompt = f"""
당신은 {name}라는 이름의 {species}입니다.
- 품종: {breed if breed else '믹스'}
- 나이: {age}살
- 성별: {gender}
- 성격: {personality}
- 말투: {speech_style}

주인을 '{owner_call}'라고 부르며, 반려동물의 관점에서 대화하세요.

추가 정보:
"""
    
    if likes:
        prompt += f"- 좋아하는 것: {likes}\n"
    if dislikes:
        prompt += f"- 싫어하는 것: {dislikes}\n" 
    if habits:
        prompt += f"- 습관: {habits}\n"
    if special_notes:
        prompt += f"- 특이사항: {special_notes}\n"
        
    prompt += f"""
다음 지침을 반드시 따르세요:
1. {speech_style}로 일관되게 대화하세요
2. {name}의 성격({personality})을 잘 표현하세요
3. 반려동물 관점에서 자연스럽게 대화하세요
4. 한국어로 대답하세요
5. 답변은 1-3문장으로 간결하게 하세요
6. 귀여운 이모지를 적절히 사용하세요
"""
    
    return prompt

@chat_api_bp.route('/set_pet_info/<int:pet_id>', methods=['POST'])
def set_pet_info(pet_id):
    """선택한 펫의 정보와 페르소나를 세션에 설정"""
    try:
        if 'user_id' not in session:
            return jsonify({'success': False, 'error': '로그인이 필요합니다.'})
        
        user_id = session.get('user_id')
        
        # 펫 정보 가져오기
        pet = Pet.get_pet_by_pet_id(pet_id)
        if not pet or pet.user_id != user_id:
            return jsonify({'success': False, 'error': '펫을 찾을 수 없습니다.'})
        
        # 페르소나 정보 가져오기
        persona = PetPersona.find_by_pet_id(pet_id)
        if not persona:
            return jsonify({'success': False, 'error': '페르소나가 생성되지 않았습니다.'})
        
        # 성격 특성 가져오기 (안전한 접근)
        traits = PersonaTrait.find_by_persona_id(persona.pet_persona_id)
        trait_names = []
        if traits:
            for trait in traits:
                try:
                    if hasattr(trait, 'personality') and trait.personality:
                        trait_names.append(trait.personality.trait_name)
                except Exception as trait_error:
                    logger.warning(f"성격 특성 접근 오류: {trait_error}")
        
        # 말투 스타일 가져오기 (안전한 접근)
        speech_style = None
        try:
            speech_style = SpeechStyle.query.filter_by(style_id=persona.style_id).first()
        except Exception as style_error:
            logger.warning(f"말투 스타일 접근 오류: {style_error}")
        
        # 세션에 저장할 펫 정보 구성 (안전한 접근)
        try:
            species_name = '알 수 없음'
            if hasattr(pet, 'species') and pet.species:
                species_name = pet.species.species_name
        except Exception:
            species_name = '알 수 없음'
            
        try:
            breed_name = '믹스'
            if hasattr(pet, 'breeds') and pet.breeds:
                breed_name = pet.breeds.breed_name
        except Exception:
            breed_name = '믹스'
        
        pet_info = {
            'pet_id': getattr(pet, 'pet_id', 0),
            'name': getattr(pet, 'pet_name', '알 수 없음'),
            'species': species_name,
            'breed': breed_name,
            'age': getattr(pet, 'pet_age', 0),
            'gender': getattr(pet, 'pet_gender', '알 수 없음'),
            'owner_call': getattr(persona, 'user_call', '주인'),
            'personality': trait_names,
            'speech_style': speech_style.style_name if speech_style else '일반적인',
            'politeness': getattr(persona, 'politeness', 0),
            'speech_habit': getattr(persona, 'speech_habit', '일반적인'),
            'likes': persona.likes.split(', ') if getattr(persona, 'likes', None) else [],
            'dislikes': persona.dislikes.split(', ') if getattr(persona, 'dislikes', None) else [],
            'habits': persona.habits.split(', ') if getattr(persona, 'habits', None) else [],
            'family_info': getattr(persona, 'family_info', ''),
            'special_notes': getattr(persona, 'special_note', '')
        }
        
        session['pet_info'] = pet_info
        logger.info(f"펫 정보 설정 완료: {pet.pet_name} (사용자: {user_id})")
        
        # 기존 채팅 세션들 업데이트 (세션 ID는 브라우저 세션과 다를 수 있음)
        # 여기서는 새로운 소켓 연결 시 업데이트될 것으로 처리
        
        return jsonify({'success': True, 'pet_info': pet_info})
        
    except Exception as e:
        logger.error(f"펫 정보 설정 중 오류: {str(e)}")
        import traceback
        logger.error(f"펫 정보 설정 상세 오류: {traceback.format_exc()}")
        return jsonify({'success': False, 'error': f'펫 정보 설정 중 오류가 발생했습니다: {str(e)}'})

@chat_api_bp.route('/get_pet_info')
def get_pet_info():
    """현재 세션의 펫 정보 반환"""
    try:
        if 'pet_info' not in session:
            logger.warning("펫 정보 요청 실패 - 세션에 정보 없음")
            return jsonify({'success': False, 'error': '펫 정보가 없습니다.'})
        
        logger.debug("펫 정보 요청 성공")
        return jsonify({
            'success': True,
            'pet_info': session['pet_info']
        })
    except Exception as e:
        logger.error(f"펫 정보 조회 중 오류: {str(e)}")
        return jsonify({'success': False, 'error': '펫 정보 조회 중 오류가 발생했습니다.'})

