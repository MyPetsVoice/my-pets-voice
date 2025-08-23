from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def init_db(app):
    db.init_app(app)

    # 모든 모델 import (테이블 생성을 위함)
    from app.models.base import BaseModel
    from app.models.user import User
    from app.models.pet_persona import PetPersona
    from app.models.dailycare.healthCare.healtCare import HealthCare
    from app.models.dailycare.healthCare.healthcareMedication import HealthCareMedication
    from app.models.dailycare.medicalCare.allergy import Allergy
    from app.models.dailycare.medicalCare.disease import Disease
    from app.models.dailycare.medicalCare.medication import Medication
    from app.models.dailycare.medicalCare.surgery import Surgery
    from app.models.dailycare.medicalCare.vaccination import Vaccination
    
    
    
    


    with app.app_context():
        db.create_all()

# 모델들을 import하여 다른 모듈에서 사용할 수 있도록 함
from app.models.base import BaseModel
from app.models.user import User
from app.models.pet import Pet
from app.models.pet_persona import PetPersona
from app.models.dailycare.healthCare.healtCare import HealthCare
from app.models.dailycare.healthCare.healthcareMedication import HealthCareMedication
from app.models.dailycare.medicalCare.allergy import Allergy
from app.models.dailycare.medicalCare.disease import Disease
from app.models.dailycare.medicalCare.medication import Medication
from app.models.dailycare.medicalCare.surgery import Surgery
from app.models.dailycare.medicalCare.vaccination import Vaccination
from app.models.dailycare.healthCare.todo import TodoList
    
    

__all__ = ['db', 'init_db', 'BaseModel', 'User', 'Pet', 'PetPersona', 
           'HealthCare', 'HealthCareMedication','Allergy','Disease','Medication','Surgery','Vaccination','TodoList']

