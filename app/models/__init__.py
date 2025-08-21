from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def init_db(app):
    db.init_app(app)

    # 모든 모델 import (테이블 생성을 위함)
    from app.models.base import BaseModel
    from app.models.user import User
    from app.models.petPersona import PetPersona
    

    with app.app_context():
        db.create_all()

# 모델들을 import하여 다른 모듈에서 사용할 수 있도록 함
from app.models.base import BaseModel
from app.models.user import User
from app.models.petPersona import PetPersona

__all__ = ['db', 'init_db', 'BaseModel', 'User', 'PetPersona']

