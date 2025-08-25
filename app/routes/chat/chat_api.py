from flask import Blueprint, request, jsonify, session, current_app
from flask_socketio import SocketIO, emit, join_room, leave_room
from langchain_openai import ChatOpenAI
from langchain.schema import SystemMessage, HumanMessage
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

