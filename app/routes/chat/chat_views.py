from flask import Blueprint, render_template, session, redirect, url_for, request
from app.models import Pet, PetPersona
from app.services import PetService
import logging

logger = logging.getLogger(__name__)

chat_views_bp = Blueprint('chat_views', __name__)

@chat_views_bp.route('/chat', methods=['GET'])
def chat():
    if 'user_id' not in session:
        return redirect(url_for('index'))
    
    user_id = session.get('user_id')
    user = session.get('user')
    user_nickname = user['kakao_account']['profile']['nickname']

    # 사용자의 반려동물 목록 가져오기 (페르소나가 있는 것만)
    pets_with_persona = []
    user_pets = PetService.get_pets_by_user(user_id)
    
    for pet in user_pets:
        logger.debug(f'펫 : {pet}')
        logger.debug(f'펫 아이디 : {pet.pet_id}')
        persona = PetPersona.find_persona_by_pet_id(pet.pet_id)
        logger.debug(f'딕셔너리로 변경한 페르소나 : {persona}')
        if persona:
            # Pet 정보와 Persona 정보를 합쳐서 전달
            pet_data = pet.to_dict()
            pet_data.update(persona)
            pet_data['has_persona'] = True
            pets_with_persona.append(pet_data)
            
    logger.debug(f'페르소나가 있는 펫 리스트 : {pets_with_persona}')
    return render_template('chat/chat.html', user=user_nickname, pets=pets_with_persona)

# 필요에 따라 추가 라우트