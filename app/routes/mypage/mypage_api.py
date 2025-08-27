from flask import Blueprint, jsonify, request, session
from app.models import Pet, PetSpecies, PetBreed, PetPersona, SpeechStyle, PersonalityTrait, PersonaTrait
import logging

logger = logging.getLogger(__name__)
# logger.propagate = False

mypage_api_bp = Blueprint('mypage_api', __name__)

@mypage_api_bp.route('/species/')
def get_species():
    pet_species = PetSpecies.get_all_species()
    species = [species.to_dict() for species in pet_species]
    # logger.debug(f'species :  {species}')

    return jsonify({'data' : species})

@mypage_api_bp.route('/breeds/<species_id>')
def get_breeds_by_species(species_id):
    pet_breeds = PetBreed.get_by_species(species_id)
    breeds = [breed.to_dict() for breed in pet_breeds]
    logger.debug(f'선택된 speices id : {species_id}')
    logger.debug(f'선택된 종의 품종 : {breeds}')
    return jsonify({'data': breeds})

@mypage_api_bp.route('/add-pet/', methods=['POST'])
def add_pet():
    # formdata로 요청 받은 경우
    # pet_info = request.form
    # logger.debug(pet_info)
    # pet_name = request.form.get('pet-name')
    # pet_species = request.form.get('pet-species')
    # pet_breed = request.form.get('pet-breed')
    # pet_age = request.form.get('pet-age')
    # birthdate = request.form.get('birthdate')
    # adoption_date = request.form.get('adoption-date')
    # pet_gender = request.form.get('pet-gender')
    # is_neutered = request.form.get('is-neutered') == 'on'
    # profile_img_url = request.form.get('pet-img')

    # json으로 요청 받은 경우
    logger.debug(f"요청 메서드: {request.method}")
    logger.debug(f"Content-Type: {request.content_type}")
    logger.debug(f"요청 데이터 존재 여부: {bool(request.data)}")
    logger.debug(f"Raw 데이터: {request.data}")

    pet_info = request.get_json()
    logger.debug(f'요청받은 json 데이터 : {pet_info}')

    pet_data = {k: v for k, v in pet_info.items() if v != ''}

    user_id = session.get('user_id')
    logger.debug(f'세션에 저장된 사용자 아이디 : {user_id}')

    new_pet = Pet.create_pet(user_id, 
                #    pet_name=pet_name,
                #    pet_species=pet_species,
                #    pet_breed=pet_breed,
                #    pet_age=pet_age,
                #    birthdate=birthdate,
                #    adoption_date=adoption_date,
                #    pet_gender=pet_gender,
                #    is_neutered=is_neutered,
                #    profile_img_url=profile_img_url
                **pet_data
                 )

    logger.debug(f'새로 등록된 반려동물 : {new_pet}')


    return jsonify({'success': '반려동물이 성공적으로 등록되었습니다.'})


@mypage_api_bp.route('/pets/')
def get_pets_info():
    user_id = session.get('user_id')
    pets = Pet.find_pets_by_user_id(user_id)

    pets_info = [pet.to_dict() for pet in pets]

    logger.debug(pets_info)

    return jsonify(pets_info)

@mypage_api_bp.route('/pet-profile/<pet_id>')
def get_pet_profile(pet_id):
    pet = Pet.find_pet_by_pet_id(pet_id)
    logger.debug(pet)
    
    if pet:
        logger.debug(pet)
        return jsonify(pet)
    else:
        return jsonify({'error': 'Pet not found'}), 404


# 페르소나 생성 관련 엔드포인트
# 1. 말투 데이터 가져오기
# 2. 성격 데이터 가져오기
# 3. 페르소나 저장하기

@mypage_api_bp.route('/speech-styles/')
def get_speech_styles():
    speech_styles = SpeechStyle.get_speech_styles()
    

    speech_styles = [style.to_dict() for style in speech_styles]
    
    return jsonify(speech_styles)

@mypage_api_bp.route('/personality-traits')
def get_personality_traits():
    personality_traits = PersonalityTrait.get_traits_by_category()
    

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


@mypage_api_bp.route('/get-persona/<pet_id>')
def get_persona_by_pet_id(pet_id):

    persona = PetPersona.get_persona_info(int(pet_id))

    if persona == None:
        return jsonify({'message': '아직 페르소나가 생성되지 않았습니다.'})
    
    logger.debug(f'{pet_id}번 pet의 페르소나 정보 :{persona}')

    # persona가 존재하는지 존재하지 않는지 예외처리 필요?

    return jsonify({'pet_persona': persona})