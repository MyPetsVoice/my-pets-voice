from app.models import db, PetPersona, PersonaTrait, PersonalityTrait, SpeechStyle

class PersonaService:
    @staticmethod
    def find_by_persona_id(pet_persona_id):
        """특정 페르소나 ID로 성격 특징 목록 조회"""
        traits = PersonaTrait.query.filter_by(pet_persona_id=pet_persona_id).all()
        return [trait.to_dict() for trait in traits]
    
    @staticmethod
    def get_speech_styles():
        """모든 말투 스타일 조회"""
        return SpeechStyle.query.all()
    
    @staticmethod
    def find_by_style_id(style_id):
        """스타일 ID로 말투 스타일 조회"""
        speech_style = SpeechStyle.query.filter_by(style_id=style_id).first()
        return speech_style.to_dict()
    
    @staticmethod
    def get_traits_by_category():
        """카테고리별로 성격 특징 조회"""
        traits = PersonalityTrait.query.order_by(PersonalityTrait.category.asc()).all()
        grouped = {}

        for trait in traits:
            category = trait.category
            if category not in grouped:
                grouped[category] = []
            grouped[category].append(trait)
        
        return grouped