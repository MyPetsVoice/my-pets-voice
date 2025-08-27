from app.models import db
from app.models.base import BaseModel
import logging

logger = logging.getLogger(__name__)

class PetPersona(BaseModel):
    __tablename__ = 'pet_personas'

    pet_persona_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    pet_id = db.Column(db.Integer, db.ForeignKey('pets.pet_id'), nullable=False)

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
    pet = db.relationship('Pet', backref=db.backref('persona', uselist=False)) # uselist=False => 1:1 관계
    speech_style = db.relationship('SpeechStyle', backref=db.backref('persona', uselist=False))


    def __repr__(self):
        return f'<PetPersona {self.pet.pet_name}>'

    @classmethod
    def create_persona(cls, user_id, pet_id, **kwargs):
        existing = cls.find_by_pet_id(pet_id)
        if existing:
            raise ValueError(f'Pet Id {pet_id}에 대한 페르소나가 이미 존재합니다.')
        return cls.create(pet_id=pet_id, user_id=user_id, **kwargs)

    @classmethod
    def find_by_pet_id(cls, pet_id):
        persona = cls.query.filter_by(pet_id=pet_id).first()
        logger.debug(f'find by pet id로 찾은 페르소나 객체 : {persona}')
        
        if persona:
            return persona.to_dict()

        return persona # 결과 없음..
    
    @classmethod
    def get_persona_info(cls, pet_id):
        persona = PetPersona.find_by_pet_id(pet_id)
        logger.debug(f'페르소나 기본 정보 : {persona}')

        persona_id = persona['pet_persona_id']
        logger.debug(f'페르소나 아이디 : {persona_id}')

        traits = PersonaTrait.find_by_persona_id(persona_id)
        logger.debug(f'성격 및 특징 : {traits}')

        style_id = persona['style_id']
        speech_style = SpeechStyle.find_by_style_id(style_id)
        speech_style_name = speech_style['style_name']
        logger.debug(f'말투 : {speech_style_name} ')

        persona_info = persona
        persona_info['traits'] = [trait['trait_name'] for trait in traits]
        persona_info['style_name'] = speech_style_name

        logger.debug(persona_info)
        return persona_info


    def get_persona_prompt(self):
        """대화 챗봇 시스템 프롬프트로 사용될 반려동물 정보를 반환"""
        prompt = f"너는 사용자의 반려동물인 {self.pet_name}이야. "
        
        if self.pet_species:
            prompt += f"나는 {self.pet_species}이고, "
        
        if self.pet_breed:
            prompt += f"{self.pet_breed} 품종이야. "
        
        if self.pet_age:
            prompt += f"나이는 {self.pet_age}살이야. "
        
        if self.personality_traits:
            prompt += f"내 성격은 {self.personality_traits}이야. "
        
        if self.favorite_activities:
            prompt += f"좋아하는 활동은 {self.favorite_activities}이야. "
        
        if self.behavioral_notes:
            prompt += f"특이사항: {self.behavioral_notes} "
            
        return prompt

class PersonaTrait(BaseModel):
    __tablename__ = 'persona_traits'

    persona_trait_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    pet_persona_id = db.Column(db.Integer, db.ForeignKey('pet_personas.pet_persona_id'), nullable=False)
    trait_id = db.Column(db.Integer, db.ForeignKey('personality_traits.trait_id'), nullable=False)

    persona = db.relationship('PetPersona', backref='persona_traits')
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
    def find_by_persona_id(cls, pet_persona_id):
        traits = cls.query.filter_by(pet_persona_id=pet_persona_id).all()
        return [trait.to_dict() for trait in traits]

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
    def get_traits_by_category(cls):
        traits = cls.query.order_by(cls.category.asc()).all()
        grouped = {}

        for trait in traits:
            category = trait.category
            if category not in grouped:
                grouped[category] = []
            grouped[category].append(trait)
        
        return grouped
    
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
    def get_speech_styles(cls):
        return cls.query.all()
    
    @classmethod
    def find_by_style_id(cls, style_id):
        speech_style = cls.query.filter_by(style_id=style_id).first()
        return speech_style.to_dict()
    
    @classmethod
    def create_speech_style(cls, style_name, style_description=None, example_phrases=None):
        return cls.create(style_name=style_name, description=style_description, example_phrases=example_phrases)

    def to_dict(self):
        return {'style_id': self.style_id,
                'style_name': self.style_name}
    

