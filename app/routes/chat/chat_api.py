from flask import Blueprint, request, jsonify, session, Response
from flask_socketio import SocketIO, emit, join_room, leave_room
from app.services.chat import chat_service, _tts_service
from app.models import Pet, PetPersona
from app.services import PetService
import os
import json
import threading
import time
import asyncio # 비동기 프로그래밍을 지원하는 모듈
import logging

logger = logging.getLogger(__name__)

chat_api_bp = Blueprint('chat_api', __name__)

socketio = None  # 메인 앱에서 초기화됨

def init_socketio(app_socketio, app):
    global socketio
    socketio = app_socketio

    # SocketIO 이벤트 핸들러 등록
    @socketio.on('connect')
    def on_connect():
        logger.info(f'클라이언트 연결됨: {request.sid}')


    @socketio.on('disconnect')
    def on_disconnect():
        logger.info(f'클라이언트 연결 종료: {request.sid}')
        # 채팅 세션 삭제
        chat_service.delete_chat_session(request.sid)
        leave_room(request.sid)

    @socketio.on('join_chat')
    def join_chat(data):
        logger.debug(f'클라이언트로부터 받은 pet 정보 : {data}')
        # 이때 tts 정보도 받을까?

        # 세션에 펫 정보 있는지 확인
        if 'pet_info' not in session:
            logger.warning(f'펫 정보가 세션에 없음. {request.sid}')
            emit('error', {'message': '펫 정보가 없습니다. 다시 설정해주세요.'})
            return
        
        pet_info = session['pet_info']
        # 채팅 세션 생성
        chat_service.create_chat_session(request.sid, pet_info) # 메서드 구현 필요
        # 채팅 세션 생성 성공 시 클라이언트에 알림
        emit('chat_ready', {
            'success': True,
            'message': '채팅 준비 완료',
            'pet_name': pet_info.get('pet_name', '펫')
        })

        join_room(request.sid)
        pet_name = pet_info.get('pet_name', '알 수 없음')
        logger.info(f'펫 정보 로드됨: {pet_name} (세션: {request.sid})')


    @socketio.on('send_message')
    def handle_message(data):
        logger.debug(f'사용자 메시지로 받은 내용 :  {data}')
        
        # 입력값 검증
        if not data or 'message' not in data:
            logger.warning(f'잘못된 메시지 형식: {data}')
            emit('error', {'message': '메시지 형식이 올바르지 않습니다.'})
            return
        
        user_message = data['message'].strip()
        logger.debug(f'사용자 메시지를 받음 : {user_message}')

        if not user_message:
            emit('error', {'message': '빈 메시지는 보낼 수 없습니다.'})
            return
        
        if len(user_message) > 1000: # 메시지 길이 제한
            emit('error', {'message': '메세지가 너무 깁니다. (최대 1000자)'})
            return
        
        try:
            client_sid = request.sid
            chat_session = chat_service.get_chat_session(client_sid) # 메서드 구현 필요
            if not chat_session:
                logger.error(f'존재하지 않는 채팅 세션: {client_sid}')
                emit('error', {'message': '채팅 세션이 존재하지 않습니다.'})
                return
            
            pet_info = session['pet_info'] ## 세션에서 가져오면 안 되고.. 아님.. 그 전에 가져온 걸 저장해뒀으면 괜찮

            logger.debug(f'메시지 수신 - 사용자: {user_message[:50]}...')

            # 사용자 메시지 브로드캐스트
            emit('user_message', {'message': user_message})

            # 타이핑 인디케이터 표시
            emit('bot_typing', {'pet_name': pet_info['pet_name']})

            # 백그라운드에서 AI 응답 생성
            def generate_response():
                try:
                    pet_id = pet_info.get('pet_id')
                    if not pet_id:
                        # pet_id가 없는 경우 어떻게 처리함? 임시 정보 생성...? 굳이..? 왜? 걍 잘못됐다 그러든가...
                        return 'pet_id가 없음'
                    else:
                        response_data = chat_service.chat(pet_info, user_message, client_sid)


                    if not response_data['success']:
                        logger.error(f'AI 응답 생성 실패: {response_data.get("error", "알 수 없는 오류")}')
                        bot_message = response_data.get("response", "죄송해요, 지금은 대답하기 어려워요...")
                    else:
                        bot_message = response_data['response']
                        logger.debug(f'AI 응답 : {bot_message}')

                    
                    if not bot_message:
                        logger.warning('AI 응답이 비어있습니다.')
                        bot_message = '죄송해요, 지금은 말하기 어려워요....'

                    # 클라이언트에게 응답 전송
                    socketio.emit(
                        'bot_response', {
                            'message': bot_message,
                            'pet_name': pet_info.get('pet_name', '펫')
                            }, 
                        room=client_sid)
                    
                    logger.debug(f'AI 응답 - 길이: {len(bot_message)}자')

                except Exception as e:
                    logger.error(f'AI 응답 생성 중 오류: {str(e)}')
                    socketio.emit(
                        'error', {
                            'message': '죄송해요.. 지금은 대답하기 어려워용'
                        }, room=client_sid)

            # 별도 스레드에서 응답 생성
            threading.Thread(target=generate_response, daemon=True).start()
        
        except Exception as e:
            logger.error(f'메시지 처리 중 오류: {str(e)}')
            emit('error', {'message': '메시지 처리 중 오류가 발생했습니다.'})

    @socketio.on('reset_chat')
    def handle_reset():
        try:
            client_sid = request.sid
            if chat_service.reset_chat_history(client_sid):
                logger.info(f'채팅 초기화: {client_sid}')
                emit('chat_reset', {'message': '대화가 초기화되었습니다.'})
            else:
                emit('error', {'message': '채팅 세션을 찾을 수 없습니다.'})
        
        except Exception as e:
            logger.error(f'채팅 초기화 중 오류: {str(e)}')
            emit('error', {'message': '채팅 초기화 중 오류가 발생했습니다.'})




@chat_api_bp.route('/get_persona/<pet_id>')
def get_persona_info(pet_id):
    try:
        logger.debug(f'선택된 반려동물의 아이디 : {pet_id}')
        # 펫 기본정보와 페르소나 정보 모두 가져와서 전달
        pet_info = PetService.get_pet(pet_id)
        logger.debug(f'펫 아이디 {pet_id}의 기본 정보 : {pet_info}')

        # PetPersona.get_persona_info는 classmethod이므로 그대로 사용
        persona_info = PetPersona.get_persona_info(pet_id)
        logger.debug(f'펫 아이디 {pet_id}의 페르소나 정보 : {persona_info}')

        persona_info.update(pet_info)
        session['pet_info'] = persona_info

        return jsonify({'success': True, 'persona_info': persona_info})

    except Exception as e:
        logger.error(f'페르소나 정보 조회 중 오류: {str(e)}')
        return jsonify({'success': False, 'error': '페르소나 정보 조회 중 오류가 발생했습니다.'})

@chat_api_bp.route('/chat/tts', methods=['POST'])
def generate_tts():
    data = request.get_json()
    
    if data is None:
        return jsonify({'message': 'tts 설정 정보가 없습니다.'})
    
    text = data.get('text')
    voice = data.get('voice', 'alloy')

    def generate():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        try:
            async def collect_chunks():
                chunks= []
                async for chunk in _tts_service.generate_speech_stream(voice, text):
                    chunks.append(chunk)
                return b''.join(chunks)
            
            # 비동기 제너레이터의 모든 데이터를 수집
            audio_data = loop.run_until_complete(collect_chunks())

            # 청크 단위로 yield(동기 제너레이터)
            chunk_size = 1024
            for i in range(0, len(audio_data), chunk_size):
                yield audio_data[i:i + chunk_size]
        
        finally:
            loop.close

    return Response(generate(), mimetype='audio/mpeg')


@chat_api_bp.route('/get_chat_history/<session_key>')
def get_chat_history(session_key):
    try:
        history = chat_service.get_chat_history(session_key)
        return jsonify({'success': True,
                        'history': [msg.content if hasattr(msg, 'content') else str(msg) for msg in history]})

    except Exception as e:
        logger.error(f'채팅 히스토리 조회 중 오류: {str(e)}')
        return jsonify({'success': False, 'error': '히스토리 조회 중 오류가 발생했습니다.'})
