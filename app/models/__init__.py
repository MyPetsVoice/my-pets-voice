from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def init_db(app):
    db.init_app(app)

    # 모든 모델 import (테이블 생성을 위함)
    from app.models.base import BaseModel
    from app.models.user import User
    from app.models.pet import Pet, PetSpecies, PetBreed
    from app.models.pet_persona import PetPersona, PersonaTrait, PersonalityTrait, SpeechStyle
    from app.models.chat_history import ChatHistory

    with app.app_context():
        db.create_all()
        
        # 기존 init_db_with_check.py의 함수 import하여 사용
        import sys
        import os
        sys.path.append(os.path.join(os.path.dirname(app.root_path), 'app/models'))
        
        try:
            from init_db_with_check import check_and_insert_initial_data
            check_and_insert_initial_data()
        except ImportError:
            print("초기 데이터 삽입 함수를 찾을 수 없습니다. 수동으로 init_db_with_check.py를 실행해주세요.")

# 모델들을 import하여 다른 모듈에서 사용할 수 있도록 함
from app.models.base import BaseModel
from app.models.user import User
from app.models.pet import Pet, PetSpecies, PetBreed
from app.models.pet_persona import PetPersona, PersonaTrait, PersonalityTrait, SpeechStyle
from app.models.chat_history import ChatHistory

__all__ = ['db', 'init_db', 'BaseModel', 'User', 'Pet', 'PetPersona', 'PersonaTrait', 'PetSpecies', 'PetBreed', 'PersonalityTrait', 'SpeechStyle', 'ChatHistory']

