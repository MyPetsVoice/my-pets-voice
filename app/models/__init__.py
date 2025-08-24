from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def init_db(app):
    db.init_app(app)

    # 모든 모델 import (테이블 생성을 위함)
    from app.models.base import BaseModel
    from app.models.user import User
    from app.models.pet import Pet, PetSpecies, PetBreed
    from app.models.pet_persona import PetPersona, PersonaTrait, PersonalityTrait, SpeechStyle

    with app.app_context():
        db.create_all()

# 모델들을 import하여 다른 모듈에서 사용할 수 있도록 함
from app.models.base import BaseModel
from app.models.user import User
from app.models.pet import Pet, PetSpecies, PetBreed
from app.models.pet_persona import PetPersona, PersonaTrait, PersonalityTrait, SpeechStyle

__all__ = ['db', 'init_db', 'BaseModel', 'User', 'Pet', 'PetPersona', 'PersonaTrait', 'PetSpecies', 'PetBreed', 'PersonalityTrait', 'SpeechStyle']

