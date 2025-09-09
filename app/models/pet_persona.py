from app.models import db
from app.models.base import BaseModel
import logging

logger = logging.getLogger(__name__)

class PetPersona(BaseModel):
    __tablename__ = 'pet_personas'

    pet_persona_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    pet_id = db.Column(db.Integer, db.ForeignKey('pets.pet_id', ondelete='CASCADE'), nullable=False)

    user_call = db.Column(db.String(50), nullable=False)
    style_id = db.Column(db.String, db.ForeignKey('speech_styles.style_id'), nullable=False)
    politeness = db.Column(db.String, nullable=False)
    speech_habit = db.Column(db.Text)
    likes = db.Column(db.Text)
    dislikes = db.Column(db.Text)
    habits = db.Column(db.Text)
    family_info = db.Column(db.Text)
    special_note = db.Column(db.Text)


    user = db.relationship('User', backref='pet_personas')
    # pet 관계는 Pet 모델에서 정의됨 (cascade 적용)
    speech_style = db.relationship('SpeechStyle', backref=db.backref('persona', uselist=False))
    # Diary와의 관계 - PetPersona 삭제시 Diary도 함께 삭제
    diaries = db.relationship('Diary', backref='pet_persona', cascade='all, delete-orphan')


    def __repr__(self):
        return f'<PetPersona {self.pet.pet_name}>'

    @classmethod
    def create_persona(cls, user_id, pet_id, **kwargs):
        existing = cls.find_persona_by_pet_id(pet_id)
        if existing:
            raise ValueError(f'Pet Id {pet_id}에 대한 페르소나가 이미 존재합니다.')
        return cls.create(pet_id=pet_id, user_id=user_id, **kwargs)
    
    @classmethod
    def update_persona(cls, pet_id, persona_info):
        # 객체를 가져와야 함 (딕셔너리가 아니라)
        persona = cls.query.filter_by(pet_id=pet_id).first()
        
        if not persona:
            raise ValueError(f'Pet Id {pet_id}에 대한 페르소나를 찾을 수 없습니다.')

        for k, v in persona_info.items():
            setattr(persona, k, v)

        db.session.commit()
        return persona

    @classmethod
    def find_persona_by_pet_id(cls, pet_id):
        persona = cls.query.filter_by(pet_id=pet_id).first()
        logger.debug(f'find by pet id로 찾은 페르소나 객체 : {persona}')
        
        if persona:
            return persona.to_dict()

        return persona # 결과 없음..
    
    @classmethod
    def get_persona_info(cls, pet_id):
        persona = PetPersona.find_persona_by_pet_id(pet_id)
        logger.debug(f'페르소나 기본 정보 : {persona}')

        if not persona:
            return persona

        persona_id = persona['pet_persona_id']
        logger.debug(f'페르소나 아이디 : {persona_id}')

        # PersonaTrait.find_by_persona_id가 서비스로 이동되어 임시로 직접 쿼리 사용
        traits = PersonaTrait.query.filter_by(pet_persona_id=persona_id).all()
        traits = [trait.to_dict() for trait in traits]
        logger.debug(f'성격 및 특징 : {traits}')

        style_id = persona['style_id']
        # SpeechStyle.find_by_style_id가 서비스로 이동되어 임시로 직접 쿼리 사용
        speech_style = SpeechStyle.query.filter_by(style_id=style_id).first()
        speech_style_data = speech_style.to_dict() if speech_style else {}
        speech_style_name = speech_style_data.get('style_name', '') if speech_style_data else ''
        logger.debug(f'말투 : {speech_style_name} ')

        persona_info = persona
        persona_info['traits'] = traits
        persona_info['style_name'] = speech_style_name

        logger.debug(persona_info)
        return persona_info


class PersonaTrait(BaseModel):
    __tablename__ = 'persona_traits'

    persona_trait_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    pet_persona_id = db.Column(db.Integer, db.ForeignKey('pet_personas.pet_persona_id', ondelete='CASCADE'), nullable=False)
    trait_id = db.Column(db.Integer, db.ForeignKey('personality_traits.trait_id'), nullable=False)

    persona = db.relationship('PetPersona', backref=db.backref('persona_traits', cascade='all, delete-orphan'))
    personality = db.relationship('PersonalityTrait', backref='persona_traits')

    @classmethod
    def create_persona_trait(cls, persona_id, trait_ids):
        created = []
        for trait_id in trait_ids:
            trait = cls.create(pet_persona_id=persona_id, trait_id=trait_id)
            print(trait)
            created.append(trait)
        return created
    
    @classmethod
    def update_traits(cls, persona_id, trait_ids):
        # 페르소나 아이디에 해당하는거 싹 다 지우고, 새로 싹 다 삽입
        traits = cls.query.filter_by(pet_persona_id=persona_id).all()

        for trait in traits:
            trait.delete()
            
        updated = cls.create_persona_trait(persona_id, trait_ids)
        return updated


    def to_dict(self):
        trait_name = self.personality.trait_name
        return {'trait_id': self.trait_id, 'trait_name': trait_name}



class PersonalityTrait(BaseModel):
    __tablename__ = 'personality_traits'

    trait_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    trait_name = db.Column(db.String(50), unique=True, nullable=False)
    category = db.Column(db.String(50))

    def __repr__(self):
        return f'<PersonalityTrait {self.trait_name}>'
    
    
    @classmethod
    def create_trait(cls, trait_name, category):
        return cls.create(trait_name=trait_name, category=category)
    
    def to_dict(self):
        return {'trait_id': self.trait_id, 'trait_name': self.trait_name, 'category': self.category}


class SpeechStyle(BaseModel):
    __tablename__ = 'speech_styles'

    style_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    style_name = db.Column(db.String(50), unique=True, nullable=False)
    style_description = db.Column(db.Text)
    example_phrases = db.Column(db.Text)

    def __repr__(self):
        return f'<SpeechStyle {self.style_name}>'
    
    
    
    @classmethod
    def create_speech_style(cls, style_name, style_description=None, example_phrases=None):
        return cls.create(style_name=style_name, description=style_description, example_phrases=example_phrases)

    def to_dict(self):
        return {'style_id': self.style_id,
                'style_name': self.style_name}
    

