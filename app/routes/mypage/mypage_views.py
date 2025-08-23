from flask import Blueprint, render_template, request, jsonify, session
from app.models.pet import Pet
from app.models.pet_persona import PetPersona
from app.models import db
import json

mypage_views_bp = Blueprint('mypage_views', __name__)

# 동물 종류별 품종 데이터
ANIMALS_DATA = {
    "개": {
        "소형견": ["치와와", "요크셔테리어", "포메라니안", "말티즈", "시츄", "페키니즈", "파피용", "토이푸들", "미니어처 닥스훈트", "보스턴테리어"],
        "중소형견": ["퍼그", "프렌치 불독", "캐벌리어 킹 찰스 스패니얼", "비글", "코커스패니얼", "웰시코기", "시바견", "진돗개"],
        "중형견": ["보더콜리", "스피츠", "슈나우저", "불테리어"],
        "대형견": ["골든 리트리버", "래브라도 리트리버", "독일 셰퍼드", "허스키", "로트와일러", "그레이트 데인", "세인트 버나드", "도베르만"]
    },
    "고양이": [
        "코리안 숏헤어", "아메리칸 숏헤어", "브리티시 숏헤어", "러시안 블루", "샴고양이", 
        "아비시니안", "벵갈고양이", "스코티시 폴드", "먼치킨", "렉돌", "페르시안", 
        "메인쿤", "노르웨이 숲고양이", "터키시 앙고라", "히말라얀", "사이베리안"
    ],
    "설치류": [
        "골든햄스터", "드워프햄스터", "로보로브스키햄스터", "기니피그", "친칠라", 
        "네덜란드드워프토끼", "롭이어토끼", "앙고라토끼", "페럿", "다람쥐"
    ],
    "소동물": ["고슴도치", "슈가글라이더"],
    "조류": [
        "코카투", "아마존앵무새", "모란앵무", "사랑앵무", "왕관앵무", "금강앵무", 
        "회색앵무", "카나리아", "십자매", "문조", "자바참새"
    ],
    "거북이": ["러시안토터스", "헤르만리쿠거북", "붉은귀거북", "노란배거북"]
}
# 성격 태그 데이터
PERSONALITY_TRAITS = [
    "활발한", "온순한", "장난기 많은", "차분한", "호기심 많은", "겁 많은", "용감한", "애교 많은",
    "독립적인", "사교적인", "조용한", "에너지 넘치는", "똑똑한", "고집센", "충성스러운", "보호적인",
    "민감한", "친근한", "경계심 많은", "느긋한"
]

# 말투 옵션
SPEECH_STYLES = [
    "귀여운 말투", "애교있는 말투", "시크한 말투", "천진난만한 말투", "의젓한 말투", 
    "장난스러운 말투", "차분한 말투", "활발한 말투"
]







@mypage_views_bp.route('/mypage')
def mypage():
    return render_template('mypage/mypage.html', 
                           animals_data=ANIMALS_DATA,
                           personality_traits=PERSONALITY_TRAITS,
                           speech_styles=SPEECH_STYLES)


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
        
        # 세션에 펫 정보 저장 (채팅에서 사용)
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

