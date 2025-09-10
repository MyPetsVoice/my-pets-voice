import logging
import os
from datetime import datetime
from flask import Blueprint, jsonify, request, session
from werkzeug.utils import secure_filename
from app.models import Pet, PetSpecies, PetBreed, PetPersona, SpeechStyle, PersonalityTrait, PersonaTrait
from app.services import PetService, PersonaService, file_uploader

logger = logging.getLogger(__name__)
# logger.propagate = False

mypage_api_bp = Blueprint('mypage_api', __name__)

@mypage_api_bp.route('/user-profile/')
def get_user_profile():
    user = session['user']['kakao_account']
    logger.debug(user)

    return jsonify({'user': user})


@mypage_api_bp.route('/species/')
def get_species():
    pet_species = PetService.get_all_species()
    species = [species.to_dict() for species in pet_species]
    # logger.debug(f'species :  {species}')

    return jsonify({'data' : species})


@mypage_api_bp.route('/breeds/<species_id>')
def get_breeds_by_species(species_id):
    pet_breeds = PetService.get_breeds_by_species(species_id)
    breeds = [breed.to_dict() for breed in pet_breeds]
    logger.debug(f'선택된 speices id : {species_id}')
    return jsonify({'data': breeds})



@mypage_api_bp.route('/add-pet/', methods=['POST'])
def add_pet():
    pet_info = request.form
    imgfile = request.files['profile_img_url']
    logger.debug(f'요청받은 form 데이터 : {pet_info}')
    logger.debug(f'요청받은 pet profile image : {imgfile}')

    # 이미지 저장
    file_url = file_uploader.save_file(imgfile, 'pet')

    # 이미지 저장경로를 db에 저장

    date_fields = {'birthdate', 'adoption_date'}
    boolean_fields = {'is_neutered'}
    
    pet_data = {}
    for k, v in pet_info.items():
        if v != '':
            if k in date_fields:
                pet_data[k] = datetime.strptime(v, '%Y-%m-%d')
            elif k in boolean_fields:
                pet_data[k] = v.lower() == 'true'
            else:
                pet_data[k] = v
    pet_data['profile_image_url'] = file_url
    user_id = session.get('user_id')
    logger.debug(f'세션에 저장된 사용자 아이디 : {user_id}')

    new_pet = Pet.create_pet(user_id, **pet_data)  # 모델의 classmethod 사용

    logger.debug(f'새로 등록된 반려동물 : {new_pet}')

    return jsonify({'success': '반려동물이 성공적으로 등록되었습니다.'})


@mypage_api_bp.route('/pets/')
def get_pets_info():
    user_id = session.get('user_id')
    pets = PetService.get_pets_by_user(user_id)

    pets_info = [pet.to_dict() for pet in pets]

    logger.debug(pets_info)

    # 이미지 파일 보내는 로직 필요

    return jsonify(pets_info)


@mypage_api_bp.route('/pet-profile/<pet_id>')
def get_pet_profile(pet_id):
    pet = PetService.get_pet(pet_id)
    logger.debug(pet)
    
    if pet:
        logger.debug(pet)
        return jsonify(pet)
    else:
        return jsonify({'error': 'Pet not found'}), 404


@mypage_api_bp.route('/delete-pet/<pet_id>', methods=['DELETE'])
def delete_pet(pet_id):
    pet = Pet.delete_pet_by_pet_id(pet_id)  # 모델의 classmethod 사용
    logger.debug(f'삭제된 펫 : {pet}')    
    
    return jsonify({'message':'삭제 완료'})


@mypage_api_bp.route('/update-pet/<pet_id>', methods=['PUT'])
def update_pet(pet_id):
    pet_info = request.form
    imgfile = request.files.get('profile_img_url')

    date_fields = {'birthdate', 'adoption_date'}
    boolean_fields = {'is_neutered'}
    
    pet_data = {}
    for k, v in pet_info.items():
        if v != '':
            if k in date_fields:
                pet_data[k] = datetime.strptime(v, '%Y-%m-%d')
            elif k in boolean_fields:
                pet_data[k] = v.lower() == 'true'
            else:
                pet_data[k] = v
    
    # 이미지가 업로드된 경우 처리
    if imgfile and imgfile.filename:
        file_url = file_uploader.save_file(imgfile, 'pet')
        pet_data['profile_image_url'] = file_url
    
    pet = Pet.update_pet_by_pet_id(pet_id, pet_data)  # 모델의 classmethod 사용
    logger.debug(f'수정된 펫 : {pet}')

    return jsonify({'success': '수정 완료'})


# 페르소나 생성 관련 엔드포인트
# 1. 말투 데이터 가져오기
# 2. 성격 데이터 가져오기
# 3. 페르소나 저장하기

@mypage_api_bp.route('/speech-styles/')
def get_speech_styles():
    speech_styles = PersonaService.get_speech_styles()
    speech_styles = [style.to_dict() for style in speech_styles]
    
    return jsonify(speech_styles)

@mypage_api_bp.route('/personality-traits')
def get_personality_traits():
    personality_traits = PersonaService.get_traits_by_category()
    
    # 각 카테고리의 trait 객체들을 to_dict()로 변환
    for category in personality_traits:
        personality_traits[category] = [trait.to_dict() for trait in personality_traits[category]]
    
    return jsonify(personality_traits)


@mypage_api_bp.route('/save-persona/<pet_id>', methods=['POST'])
def save_persona(pet_id):

    user_id = session.get('user_id')
    logger.debug(f'ㅍ르소나 생성할 pet_id : {pet_id}')
    
    persona_info = request.get_json()
    logger.debug(f'저장해야할 페르소나 정보 : {persona_info}')

    trait_ids = persona_info['trait_id']
    logger.debug(f'페르소나의 성격 및 특징들 : {trait_ids}')

    persona = {k: v for k, v in persona_info.items() if k != 'trait_id'}
    logger.debug(f'PetPersona에 저장될 정보들 : {persona}')

    new_persona = PetPersona.create_persona(user_id, pet_id, **persona)
    persona_id = new_persona.pet_persona_id
    new_traits = PersonaTrait.create_persona_trait(persona_id, trait_ids)
    logger.debug(new_traits)

    return jsonify({'success': '성공적으로 페르소나가 생성되었습니다.'})


@mypage_api_bp.route('/update-persona/<pet_id>', methods=['PUT'])
def update_persona(pet_id):
    persona = request.get_json()
    logger.debug(f'수정할 페르소나 정보 : {persona}')

    traits = persona['trait_id']
    persona_info = {k:v for k,v in persona.items() if k != 'trait_id'}
    
    updated_persona = PetPersona.update_persona(pet_id, persona_info)
    logger.debug(f'수정된 페르소나 : {updated_persona}')

    persona_id = updated_persona.pet_persona_id
    updated_traits = PersonaTrait.update_traits(persona_id, traits)
    logger.debug(updated_traits)
    
    return jsonify({'success': '수정 완료'})


@mypage_api_bp.route('/get-persona/<pet_id>')
def get_persona_by_pet_id(pet_id):

    persona = PetPersona.get_persona_info(int(pet_id))

    if persona == None:
        return jsonify({'message': '아직 페르소나가 생성되지 않았습니다.'})
    
    logger.debug(f'{pet_id}번 pet의 페르소나 정보 :{persona}')

    # persona가 존재하는지 존재하지 않는지 예외처리 필요?

    return jsonify({'pet_persona': persona})