from flask import Blueprint, render_template, session, redirect, url_for, request
from app.models import Pet, PetPersona

chat_views_bp = Blueprint('chat_views', __name__)

@chat_views_bp.route('/chat', methods=['GET'])
def chat():
    if 'user_id' not in session:
        return redirect(url_for('index'))
    
    user_id = session.get('user_id')
    
    # 사용자의 반려동물 목록 가져오기 (페르소나가 있는 것만)
    pets_with_persona = []
    user_pets = Pet.get_pets_by_user_id(user_id)
    
    for pet in user_pets:
        persona = PetPersona.find_by_pet_id(pet.pet_id)
        if persona:
            pet_data = pet.to_dict()
            pet_data['has_persona'] = True
            pets_with_persona.append(pet_data)
    
    return render_template('chat/chat.html', pets=pets_with_persona)

# 필요에 따라 추가 라우트