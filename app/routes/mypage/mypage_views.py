from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for
from app.models.pet import Pet
from app.models.pet_persona import PetPersona
from app.models import db
import json

mypage_views_bp = Blueprint('mypage_views', __name__)


@mypage_views_bp.route('/mypage')
def mypage():
    user = session.get('user')
    if user:
        user_nickname = user['kakao_account']['profile']['nickname']
        return render_template('mypage/mypage.html', user=user_nickname)

    return redirect(url_for('index')) 


@mypage_views_bp.route('/create_pet', methods=['POST'])
def create_pet():
    try:
        # 폼 데이터 가져오기
        name = request.form.get('name')
        species = request.form.get('species') 
        breed = request.form.get('breed') or request.form.get('customBreed')
        age = request.form.get('age')
        gender = request.form.get('gender')
        owner_call = request.form.get('owner_call')
        
        # 성격 데이터 처리
        personality = request.form.getlist('personality')
        personality_str = ','.join(personality) if personality else ''
        
        # 나머지 정보
        speech_style = request.form.get('speech_style')
        likes = request.form.get('likes', '')
        dislikes = request.form.get('dislikes', '')
        habits = request.form.get('habits', '')
        special_notes = request.form.get('special_notes', '')
        
        # 필수 필드 검증
        if not all([name, species, age, gender, owner_call, speech_style]):
            return jsonify({'success': False, 'error': '필수 정보를 모두 입력해주세요.'})
        
        # 사용자 ID (임시로 1로 설정, 실제로는 세션에서 가져와야 함)
        user_id = session.get('user_id', 1)
        
        # Pet 객체 생성
        pet = Pet.create_pet(
            user_id=user_id,
            pet_name=name,
            pet_species=species,
            pet_breed=breed,
            pet_age=int(age),
            pet_gender=gender
        )
        
        # PetPersona 객체 생성
        persona = PetPersona.create_persona(
            pet_id=pet.pet_id,
            user_id=user_id,
            personality_traits=personality_str,
            speaking_style=speech_style,
            user_nickname=owner_call,
            favorite_activities=likes,
            dislikes=dislikes,
            habits=habits,
            special_note=special_notes
        )
        
        # 세션에 펫 정보 저장 (채팅에서 사용) -------> 수정 필요
        pet_info = {
            'pet_id': pet.pet_id,
            'name': pet.pet_name,
            'species': pet.pet_species,
            'breed': pet.pet_breed,
            'age': pet.pet_age,
            'gender': pet.pet_gender,
            'owner_call': owner_call,
            'personality': personality,
            'speech_style': speech_style,
            'likes': likes.split(',') if likes else [],
            'dislikes': dislikes.split(',') if dislikes else [],
            'habits': habits.split(',') if habits else [],
            'special_notes': special_notes
        }
        
        session['pet_info'] = pet_info
        
        return jsonify({'success': True})
        
    except ValueError as e:
        return jsonify({'success': False, 'error': str(e)})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': '데이터베이스 오류가 발생했습니다.'})

