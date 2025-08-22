from flask import Blueprint, request, jsonify, session
from flask_socketio import SocketIO, emit, join_room, leave_room
from langchain_openai import ChatOpenAI
from langchain.schema import SystemMessage, HumanMessage
from app.models.pet_persona import PetPersona
from app.models.pet import Pet
from dotenv import load_dotenv
import os
import json
import threading
import time

load_dotenv()

chat_api_bp = Blueprint('chat_api', __name__)

socketio = None  # 메인 앱에서 초기화됨

# OpenAI API 키 설정
openai_api_key = os.environ.get('OPENAI_API_KEY')
if not openai_api_key:
    raise ValueError("OPENAI_API_KEY 환경변수가 설정되지 않았습니다.")

# LangChain ChatOpenAI 모델 초기화
llm = ChatOpenAI(
    api_key=openai_api_key,
    model="gpt-4o-mini",
    temperature=0.8,
    max_tokens=500
)

# 채팅 세션 저장 딕셔너리
chat_sessions = {}

def init_socketio(app_socketio):
    """메인 앱에서 SocketIO 객체를 전달받아 초기화"""
    global socketio
    socketio = app_socketio
    
    # SocketIO 이벤트 핸들러들 등록
    @socketio.on('connect')
    def on_connect():
        print(f"클라이언트 연결됨: {request.sid}")
        # 세션에 펫 정보가 있는지 확인
        if 'pet_info' not in session:
            emit('error', {'message': '펫 정보가 없습니다. 다시 설정해주세요.'})
            return
        
        # 채팅 세션 초기화
        chat_sessions[request.sid] = {
            'pet_info': session['pet_info'],
            'messages': []
        }
        
        join_room(request.sid)
        print(f"펫 정보: {session['pet_info']['name']}")

    @socketio.on('disconnect')  
    def on_disconnect():
        print(f"클라이언트 연결 종료: {request.sid}")
        if request.sid in chat_sessions:
            del chat_sessions[request.sid]
        leave_room(request.sid)

    @socketio.on('send_message')
    def handle_message(data):
        user_message = data['message']
        client_sid = request.sid  # request context에서 sid 미리 저장
        
        if client_sid not in chat_sessions:
            emit('error', {'message': '채팅 세션이 존재하지 않습니다.'})
            return
            
        chat_session = chat_sessions[client_sid]
        pet_info = chat_session['pet_info']
        
        # 사용자 메시지 저장 및 브로드캐스트
        chat_session['messages'].append({'role': 'user', 'content': user_message})
        emit('user_message', {'message': user_message})
        
        # 타이핑 인디케이터 표시
        emit('bot_typing', {'pet_name': pet_info['name']})
        
        # 백그라운드에서 AI 응답 생성
        def generate_response():
            try:
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
                        messages.append(SystemMessage(content=msg['content']))
                
                # AI 응답 생성
                response = llm.invoke(messages)
                bot_message = response.content
                
                # 응답 저장
                chat_session['messages'].append({'role': 'assistant', 'content': bot_message})
                
                # 클라이언트에게 응답 전송 (미리 저장한 sid 사용)
                socketio.emit('bot_response', {
                    'message': bot_message,
                    'pet_name': pet_info['name']
                }, room=client_sid)
                
            except Exception as e:
                print(f"AI 응답 생성 중 오류: {e}")
                socketio.emit('error', {
                    'message': f'죄송해요, 지금은 대답하기 어려워요... 😔'
                }, room=client_sid)
        
        # 별도 스레드에서 응답 생성
        threading.Thread(target=generate_response).start()

    @socketio.on('reset_chat')
    def handle_reset():
        if request.sid in chat_sessions:
            chat_sessions[request.sid]['messages'] = []
            emit('chat_reset', {'message': '대화가 초기화되었습니다.'})

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

@chat_api_bp.route('/get_pet_info')
def get_pet_info():
    """현재 세션의 펫 정보 반환"""
    if 'pet_info' not in session:
        return jsonify({'success': False, 'error': '펫 정보가 없습니다.'})
    
    return jsonify({
        'success': True,
        'pet_info': session['pet_info']
    })

