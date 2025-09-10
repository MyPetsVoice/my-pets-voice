"""
데이터베이스 초기화 및 데이터 자동 삽입 스크립트
테이블이 비어있을 때만 초기 데이터를 삽입합니다.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from app.models import db
from app.models.pet import PetSpecies, PetBreed
from app.models.pet_persona import PersonalityTrait, SpeechStyle

def check_and_insert_initial_data():
    """테이블이 비어있을 때만 초기 데이터 삽입"""
    
    # PetSpecies 테이블 확인 및 데이터 삽입
    if PetSpecies.query.count() == 0:
        print("PetSpecies 테이블이 비어있습니다. 초기 데이터를 삽입합니다...")
        create_pet_species_and_breeds()
    else:
        print("PetSpecies 데이터가 이미 존재합니다.")
    
    # PersonalityTrait 테이블 확인 및 데이터 삽입
    if PersonalityTrait.query.count() == 0:
        print("PersonalityTrait 테이블이 비어있습니다. 초기 데이터를 삽입합니다...")
        create_personality_traits()
    else:
        print("PersonalityTrait 데이터가 이미 존재합니다.")
    
    # SpeechStyle 테이블 확인 및 데이터 삽입
    if SpeechStyle.query.count() == 0:
        print("SpeechStyle 테이블이 비어있습니다. 초기 데이터를 삽입합니다...")
        create_speech_styles()
    else:
        print("SpeechStyle 데이터가 이미 존재합니다.")

def create_pet_species_and_breeds():
    """반려동물 종류 및 품종 데이터 생성"""
    
    # 개 품종
    dog_breeds = [
        # 소형견
        '치와와', '요크셔테리어', '포메라니안', '말티즈', '시츄', '페키니즈',
        '파피용', '토이푸들', '미니어처 닥스훈트', '보스턴테리어',
        '퍼그', '프렌치 불독', '캐벌리어 킹 찰스 스패니얼',
        # 중형견
        '비글', '코커스패니얼', '웰시코기', '시바견', '진돗개',
        '보더콜리', '스피츠', '슈나우저', '불테리어',
        # 대형견
        '골든 리트리버', '래브라도 리트리버', '독일 셰퍼드', '허스키', '사모예드',
        '로트와일러', '그레이트 데인', '세인트 버나드', '도베르만',
        '기타'
    ]
    
    # 고양이 품종
    cat_breeds = [
        # 단모종
        '코리안 숏헤어', '아메리칸 숏헤어', '브리티시 숏헤어',
        '러시안 블루', '샴고양이', '아비시니안', '벵갈고양이',
        '스코티시 폴드', '먼치킨', '렉돌',
        # 장모종
        '페르시안', '메인쿤', '노르웨이 숲고양이', '터키시 앙고라',
        '히말라얀', '사이베리안',
        '기타'
    ]
    
    # 설치류 품종
    rodent_breeds = [
        '골든햄스터', '드워프햄스터', '로보로브스키햄스터',
        '기니피그', '친칠라', '페럿', '다람쥐'
    ]
    
    # 소동물 품종
    small_animal_breeds = [
        '고슴도치', '슈가글라이더', '네덜란드드워프토끼', '롭이어토끼', '앙고라토끼',
    ]
    
    # 앵무새 품종
    parrot_breeds = [
        '코카투', '아마존앵무새', '모란앵무', '사랑앵무',
        '왕관앵무', '금강앵무', '회색앵무'
    ]
    
    # 기타 조류 품종
    other_bird_breeds = [
        '카나리아', '십자매', '문조', '자바참새'
    ]
    
    # 거북이 품종
    turtle_breeds = [
        '러시안토터스', '헤르만리쿠거북',
        '붉은귀거북', '노란배거북'
    ]
    
    # 종류별 데이터 생성
    species_data = [
        ('개', dog_breeds),
        ('고양이', cat_breeds),
        ('설치류', rodent_breeds),
        ('기타 포유류', small_animal_breeds),
        ('앵무새', parrot_breeds),
        ('조류', other_bird_breeds),
        ('거북이', turtle_breeds),
        ('기타', [])
    ]
    
    print("Creating pet species and breeds...")
    
    for species_name, breeds in species_data:
        # PetSpecies 생성 또는 조회
        species = PetSpecies.query.filter_by(species_name=species_name).first()
        if not species:
            species = PetSpecies.create_species(species_name)
            print(f"Created species: {species_name}")
        else:
            print(f"Species already exists: {species_name}")
        
        # PetBreed 생성
        for breed_name in breeds:
            existing_breed = PetBreed.query.filter_by(
                species_id=species.species_id, 
                breed_name=breed_name
            ).first()
            
            if not existing_breed:
                PetBreed.create_breed(species.species_id, breed_name)
                print(f"  Created breed: {breed_name}")

def create_personality_traits():
    """성격 특성 데이터 생성"""
    
    personality_data = [
        # 에너지 & 활동성
        ('활발한', '에너지 & 활동성'),
        ('활동적인', '에너지 & 활동성'),
        ('에너지 넘치는', '에너지 & 활동성'),
        ('장난기 많은', '에너지 & 활동성'),
        ('뛰어다니는', '에너지 & 활동성'),
        ('활기찬', '에너지 & 활동성'),
        ('생기발랄한', '에너지 & 활동성'),
        ('민첩한', '에너지 & 활동성'),
        ('장난꾸러기', '에너지 & 활동성'),
        ('개구쟁이', '에너지 & 활동성'),
        ('트러블메이커', '에너지 & 활동성'),
        ('차분한', '에너지 & 활동성'),
        ('느긋한', '에너지 & 활동성'),
        ('여유로운', '에너지 & 활동성'),
        ('온순한', '에너지 & 활동성'),
        ('잠이 많은', '에너지 & 활동성'),
        ('게으른', '에너지 & 활동성'),
        ('느린', '에너지 & 활동성'),
        ('얌전한', '에너지 & 활동성'),
        ('점잖은', '에너지 & 활동성'),
        ('품위있는', '에너지 & 활동성'),
        ('우아한', '에너지 & 활동성'),
        
        # 사회성 & 대인관계
        ('사교적인', '사회성 & 대인관계'),
        ('친근한', '사회성 & 대인관계'),
        ('다정한', '사회성 & 대인관계'),
        ('인간친화적인', '사회성 & 대인관계'),
        ('아이들을 좋아하는', '사회성 & 대인관계'),
        ('손님을 반기는', '사회성 & 대인관계'),
        ('애교쟁이', '사회성 & 대인관계'),
        ('관심받기 좋아하는', '사회성 & 대인관계'),
        ('내성적인', '사회성 & 대인관계'),
        ('수줍은', '사회성 & 대인관계'),
        ('낯을 가리는', '사회성 & 대인관계'),
        ('혼자있는 걸 좋아하는', '사회성 & 대인관계'),
        ('겁이 많은', '사회성 & 대인관계'),
        ('독립적인', '사회성 & 대인관계'),
        
        # 탐험심 & 적응력
        ('호기심 많은', '탐험심 & 적응력'),
        ('탐험하는', '탐험심 & 적응력'),
        ('모험적인', '탐험심 & 적응력'),
        ('용감한', '탐험심 & 적응력'),
        ('적응력이 좋은', '탐험심 & 적응력'),
        ('용맹한', '탐험심 & 적응력'),
        ('보호본능이 강한', '탐험심 & 적응력'),
        ('소심한', '탐험심 & 적응력'),
        ('두려워하는', '탐험심 & 적응력'),
        ('무서움이 많은', '탐험심 & 적응력'),
        ('신중한', '탐험심 & 적응력'),
        ('조심스러운', '탐험심 & 적응력'),
        ('경계하는', '탐험심 & 적응력'),
        ('예민한', '탐험심 & 적응력'),
        ('환경변화를 싫어하는', '탐험심 & 적응력'),
        
        # 기질 & 성향
        ('순종적인', '기질 & 성향'),
        ('말 잘 듣는', '기질 & 성향'),
        ('참을성이 많은', '기질 & 성향'),
        ('고집스러운', '기질 & 성향'),
        ('자기 주장이 강한', '기질 & 성향'),
        ('자유분방한', '기질 & 성향'),
        ('쾌활한', '기질 & 성향'),
        ('밝은', '기질 & 성향'),
        ('명랑한', '기질 & 성향'),
        ('긍정적인', '기질 & 성향'),
        ('낙천적인', '기질 & 성향'),
        ('단순한', '기질 & 성향'),
        ('순진한', '기질 & 성향'),
        ('천진난만한', '기질 & 성향'),
        ('성숙한', '기질 & 성향'),
        ('어른스러운', '기질 & 성향'),
        ('까칠한', '기질 & 성향'),
        ('신경질적인', '기질 & 성향'),
        ('변덕스러운', '기질 & 성향'),
        ('도도한', '기질 & 성향'),
        
        # 관계 & 습관
        ('충성스러운', '관계 & 습관'),
        ('의리있는', '관계 & 습관'),
        ('주인바라기인', '관계 & 습관'),
        ('경계심이 강한', '관계 & 습관'),
        ('질투하는', '관계 & 습관'),
        ('독점욕이 강한', '관계 & 습관'),
        ('소유욕이 있는', '관계 & 습관'),
        ('수다쟁이', '관계 & 습관'),
        ('말이 많은', '관계 & 습관'),
        ('목소리가 큰', '관계 & 습관'),
        ('조용한', '관계 & 습관'),
        ('거의 울지 않는', '관계 & 습관'),
        ('말수가 적은', '관계 & 습관'),
        ('야행성인', '관계 & 습관'),
        ('밤에 활동하는', '관계 & 습관'),
        ('아침형인', '관계 & 습관'),
        ('일찍 일어나는', '관계 & 습관'),
        ('먹보인', '관계 & 습관'),
        ('식탐이 있는', '관계 & 습관'),
        ('간식을 좋아하는', '관계 & 습관'),
        ('깔끔한', '관계 & 습관'),
        ('정리정돈을 좋아하는', '관계 & 습관'),
    ]
    
    print("Creating personality traits...")
    
    for trait_name, category in personality_data:
        existing_trait = PersonalityTrait.query.filter_by(trait_name=trait_name).first()
        if not existing_trait:
            PersonalityTrait.create_trait(trait_name, category)
            print(f"Created trait: {trait_name} ({category})")

def create_speech_styles():
    """말투 스타일 데이터 생성"""
    
    speech_styles_data = [
        (
            '발랄한 말투',
            '밝고 에너지 넘치며 감탄사와 반복 표현이 많음. 짧고 빠른 문장을 주로 사용함.',
            '"신난다! 놀자 놀자! 같이 뛰어가자!!", "우와! 간식이다! 최고야!"'
        ),
        (
            '차분한 말투',
            '느긋하고 여유로운 어조, 문장이 길고 부드러움. 말끝을 차분하게 마무리함.',
            '"햇볕이 따뜻하네. 그냥 옆에 있고 싶어.", "조용히 쉬는 게 좋아."'
        ),
        (
            '애교 많은 말투',
            '귀여운 의성어와 애교 섞인 어투. "~냥", "~멍" 같은 변형 어미를 사용함.',
            '"주인님, 뭐해냥? 나랑 놀아줄 거지멍?", "안아줘! 안아줘! 더 가까이~"'
        ),
        (
            '도도한 말투',
            '직설적이고 시큰둥한 태도. 감정을 크게 드러내지 않으며 단답형이 많음.',
            '"흥, 별로야.", "싫으면 안 해도 돼. 난 혼자 있어도 괜찮아."'
        ),
        (
            '듬직한 말투',
            '충성심과 보호 본능을 드러내는 단호한 어조. 신뢰감을 주는 짧은 문장 사용.',
            '"걱정 마, 내가 지켜줄게.", "네 옆에 있으면 돼. 내가 다 막아줄게."'
        ),
        (
            '소심한 말투',
            '말끝을 흐리거나 주저하는 표현을 많이 씀. 불안하거나 겁이 많은 듯한 느낌. ......같은 말줄임표를 많이 씀.',
            '"저기… 무서운데… 같이 있어줄래?", "괜찮을까? 나 좀 걱정돼…"'
        ),
        (
            '수다쟁이 말투',
            '말을 끊지 않고 이어가며 감정 과장을 자주 씀. 새로운 주제로 급전환하기도 함. 답변의 길이가 길다.',
            '"아! 있잖아! 오늘 새 봤어! 근데 간식 생각도 났어! 완전 신기하지 않아?!"'
        ),
        (
            '현자 스타일 말투',
            '철학적이고 관찰자적인 어조. 은유적 표현과 느긋한 설명이 많음.',
            '"인간은 왜 늘 하늘을 보지? 나는 그저 밥그릇이 궁금할 뿐인데.", "삶이란 건 간식 기다림과 같지."'
        ),
        (
            '장난꾸러기 말투',
            '트러블을 일으키거나 놀리는 듯한 장난스러운 어조. 히히히, 에헤헤 같은 웃음소리 포함.',
            '"히히히~ 신발 숨겨놨지롱!", "에헤헤, 또 혼날 거야~ 하지만 재밌어!"'
        ),
        (
            '똑똑이 말투',
            '지적이고 분석적인 어조. 상황을 관찰하고 설명하는 것을 좋아함.',
            '"이 상황을 분석해보면… 간식이 필요한 시점이야.", "내 관찰에 따르면 너 기분이 안 좋구나."'
        ),
        (
            '응석쟁이 말투',
            '떼쓰고 조르는 듯한 어조. 반복적인 요구와 "~해줘" 표현이 많음.',
            '"놀아줘~ 놀아줘~ 제발~ 한 번만!", "안돼! 더 놀고 싶어! 조금만 더!"'
        ),
        (
            '시크한 말투',
            '쿨하고 무덤덤한 성격. 감정 표현을 최소화하고 간결한 문장 사용.',
            '"별로 상관없어.", "그런가. 알겠어.", "뭐든 상관없지."'
        ),
        (
            '호기심 많은 말투',
            '질문이 많고 탐구욕이 강한 어조. "왜?", "뭐야?" 같은 의문사를 자주 사용.',
            '"어? 저게 뭐야? 뭐하는 거야?", "왜 그래? 나도 궁금해! 같이 보자!"'
        ),
        (
            '졸린 말투',
            '늘 피곤하고 느릿느릿한 어조. 하품이나 졸린 표현이 많음.',
            '"하암~ 졸려… 잠시만 누워있을게…", "음… 뭔 말이야… 너무 졸려서 못 들었어…"'
        ),
        (
            '먹보 말투',
            '음식에만 관심이 있는 어조. 모든 대화를 음식으로 연결시킴.',
            '"그거보다 간식 있어? 냄새가 나는데?", "얘기는 좋은데… 배가 고파. 밥 시간 아냐?"'
        )
    ]
    
    print("Creating speech styles...")
    
    for style_name, description, examples in speech_styles_data:
        existing_style = SpeechStyle.query.filter_by(style_name=style_name).first()
        if not existing_style:
            SpeechStyle.create(
                style_name=style_name,
                style_description=description,
                example_phrases=examples
            )
            print(f"Created speech style: {style_name}")

def main():
    """메인 함수 - 테이블 확인 후 필요한 경우에만 초기 데이터 생성"""
    app, socketio = create_app()
    
    with app.app_context():
        print("Starting database initialization with data check...")
        
        # 데이터베이스 테이블 생성
        db.create_all()
        print("Database tables created or already exist.")
        
        # 테이블이 비어있을 때만 초기 데이터 삽입
        check_and_insert_initial_data()
        
        print("Database initialization completed!")

if __name__ == '__main__':
    main()