from flask import Blueprint, request, jsonify, session
from app.models import db
from app.models.diary import Diary, DiaryPhoto
from app.models.pet_persona import PetPersona
from app.services import DiaryService as DS
import os
from werkzeug.utils import secure_filename
from datetime import datetime

diary_api_bp = Blueprint("diary_api", __name__)

# 파일 업로드 설정
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# 전체 일기 목록 조회 
@diary_api_bp.route("/list")
def list_diaries():
    diaries = DS.get_all_diaries()
    return jsonify({
        "success": True,
        "diaries": [diary.to_dict() for diary in diaries]
    })

# 펫 페르소나의 일기 목록 조회 
@diary_api_bp.route("/list/<int:pet_persona_id>")
def list_pet_diaries(pet_persona_id):
    diaries = DS.get_by_pet_persona(pet_persona_id)
    return jsonify({
        "success": True,
        "pet_persona_id": pet_persona_id,
        "diaries": [diary.to_dict() for diary in diaries]
    })

# 사용자 일기를 AI로 반려동물 관점으로 변환
@diary_api_bp.route("/convert-ai", methods=["POST"])
def convert_to_ai():
    data = request.get_json()
    
    if not data:
        return jsonify({"success": False, "message": "데이터가 없습니다."})
    
    content = data.get('content')
    pet_persona_id = data.get('pet_persona_id')
    
    if not content:
        return jsonify({"success": False, "message": "일기 내용이 없습니다."})
    
    if not pet_persona_id:
        return jsonify({"success": False, "message": "반려동물을 선택해주세요."})
    
    # 반려동물 페르소나 정보 확인 (query 방식 그대로)
    pet_persona = PetPersona.query.get(pet_persona_id)
    if not pet_persona:
        return jsonify({"success": False, "message": "페르소나 정보를 찾을 수 없습니다."})
    
    # AI 서비스 호출
    diary_service = DiaryService()
    ai_content = diary_service.convert_to_pet_diary(content, pet_persona_id)
    
    return jsonify({
        "success": True,
        "ai_content": ai_content,
        "pet_name": pet_persona.pet.pet_name
    })

# 새 일기 생성
@diary_api_bp.route("/create", methods=["POST"])
def create_diary():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({"success": False, "message": "로그인이 필요합니다."})
    
    pet_persona_id = request.form.get('pet_persona_id')
    diary_date = request.form.get('diary_date')
    title = request.form.get('title')
    content_user = request.form.get('content_user')
    content_ai = request.form.get('content_ai')
    weather = request.form.get('weather')
    mood = request.form.get('mood')
    
    if not all([pet_persona_id, diary_date, title]):
        return jsonify({
            "success": False, 
            "message": "필수 정보를 입력해주세요."
        })
    
    # 날짜 형식 변환
    diary_date = datetime.strptime(diary_date, '%Y-%m-%d').date()
    
    # 새 일기 생성
    new_diary = Diary.create_diary(
        pet_persona_id=int(pet_persona_id),
        user_id=int(user_id),
        diary_date=diary_date,
        title=title,
        content_user=content_user,
        content_ai=content_ai,
        weather=weather,
        mood=mood
    )
    
    # 사진 처리
    photos = request.files.getlist('photos')
    if photos:
        upload_folder = os.path.join('app', 'static', 'uploads', 'diary')
        os.makedirs(upload_folder, exist_ok=True)
        
        for i, photo in enumerate(photos):
            if photo and photo.filename != '' and allowed_file(photo.filename):
                # 파일명 생성
                filename = secure_filename(photo.filename)
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                filename = f"{timestamp}_{i}_{filename}"
                
                # 파일 저장
                file_path = os.path.join(upload_folder, filename)
                photo.save(file_path)
                
                # 데이터베이스에 사진 정보 저장
                diary_photo = DiaryPhoto.create_photo(
                    diary_id=new_diary.diary_id,
                    photo_url=f"/static/uploads/diary/{filename}",
                    original_filename=photo.filename,
                    display_order=i
                )
    
    return jsonify({
        "success": True,
        "message": "일기가 성공적으로 저장되었습니다!",
        "diary_id": new_diary.diary_id,
        "diary": new_diary.to_dict()
    })

# 일기 상세 조회 
@diary_api_bp.route("/detail/<int:diary_id>")
def get_diary_detail(diary_id):
    diary = Diary.query.get(diary_id)
    if not diary:
        return jsonify({"success": False, "message": "일기를 찾을 수 없습니다."})
    
    return jsonify({
        "success": True,
        "diary": diary.to_dict()
    })

# 사용자의 모든 펫 페르소나 조회
@diary_api_bp.route("/personas")
def get_user_personas():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({"success": False, "message": "로그인이 필요합니다.", "redirect": "/auth"}), 401
    
    personas = PetPersona.query.filter_by(user_id=user_id).all()
    
    persona_list = []
    for persona in personas:
        # 안전하게 관계형 데이터 접근
        pet_species = persona.pet.species.species_name if persona.pet.species else '반려동물'
        pet_breed = persona.pet.breeds.breed_name if persona.pet.breeds else '알 수 없음'
        
        # persona_traits를 통해 성격 특성들을 가져오기
        traits = []
        if hasattr(persona, 'persona_traits'):
            traits = [trait.personality.trait_name for trait in persona.persona_traits]
        
        persona_data = {
            'pet_persona_id': persona.pet_persona_id,
            'pet_name': persona.pet.pet_name,
            'pet_species': pet_species,
            'pet_breed': pet_breed,
            'user_call': persona.user_call,
            'speech_habit': persona.speech_habit,
            'likes': persona.likes,
            'dislikes': persona.dislikes,
            'habits': persona.habits,
            'traits': traits,
            'user_profile_img': persona.user.profile_img_url if hasattr(persona.user, 'profile_img_url') else None,
            'user_nickname': persona.user.nickname if hasattr(persona.user, 'nickname') else None
        }
        persona_list.append(persona_data)
        
    return jsonify({
        "success": True,
        "personas": persona_list
    })
    
# 일기 삭제
@diary_api_bp.route("/delete/<int:diary_id>", methods=["DELETE"])
def delete_diary(diary_id):
    # 일기 조회
    diary = Diary.query.get(diary_id)
    
    # 사진 파일들 삭제
    if diary.photos:
        import os
        for photo in diary.photos:
            # 실제 파일 삭제
            file_path = os.path.join('app', photo.photo_url.lstrip('/'))
            if os.path.exists(file_path):
                os.remove(file_path)
    
    # 데이터베이스에서 일기 삭제
    diary.delete()
    
    return jsonify({
        "success": True,
        "message": "일기가 성공적으로 삭제되었습니다."
    })