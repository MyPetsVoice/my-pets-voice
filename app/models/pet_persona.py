
from app.models import db
from app.models.base import BaseModel

class PetPersona(BaseModel):
    __tablename__ = 'pet_personas'

    pet_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    pet_name = db.Column(db.String(50), nullable=False)
    pet_species = db.Column(db.String(30), nullable=False)
    pet_breed = db.Column(db.String(50))
    pet_age = db.Column(db.Integer)
    pet_gender = db.Column(db.String(10))
    personality_traits = db.Column(db.Text)
    favorite_activities = db.Column(db.Text)
    health_conditions = db.Column(db.Text)
    behavioral_notes = db.Column(db.Text)
    profile_image_url = db.Column(db.String(500))

    user = db.relationship('User', backref=db.backref('pets', lazy=True))

    def __repr__(self):
        return f'<PetPersona {self.pet_name}>'

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