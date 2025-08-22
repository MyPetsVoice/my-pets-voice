from app.models import db
from app.models.base import BaseModel

class PetPersona(BaseModel):
    __tablename__ = 'pet_personas'

    pet_persona_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    pet_id = db.Column(db.Integer, db.ForeignKey('pets.pet_id'), nullable=False)

    personality_traits = db.Column(db.Text)
    speaking_style = db.Column(db.Text)
    user_nickname = db.Column(db.String(50))
    favorite_activities = db.Column(db.Text)
    dislikes = db.Colomns(db.Text)
    habits = db.Column(db.Text)
    special_note = db.Column(db.Text)
    family_info = db.Column(db.Text)
    additional_info = db.Column(db.Text)


    user = db.relationship('User', backref='pet_personas')
    pet = db.relationship('Pet', backref=db.backref('persona', uselist=False))

    def __repr__(self):
        return f'<PetPersona {self.pet.pet_name}>'

    @classmethod
    def create_persona(cls, pet_id, user_id, **kwargs):
        existing = cls.find_by_pet_id(pet_id)
        if existing:
            raise ValueError(f'Pet Id {pet_id}에 대한 페르소나가 이미 존재합니다.')
        return cls.create(pet_id=pet_id, user_id=user_id, **kwargs)

    @classmethod
    def find_by_pet_id(cls, pet_id):
        return cls.query.filter_by(pet_id=pet_id).first()


    def get_persona_prompt(self):
        """대화 챗봇 시스템 프롬프트로 사용될 반려동물 정보를 반환"""
        prompt = f"나는 {self.pet_name}이야. "
        
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