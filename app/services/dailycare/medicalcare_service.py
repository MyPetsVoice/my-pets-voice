from app.models import db, Pet
from app.models import Medication
from app.models import Allergy
from app.models import Disease
from app.models import Surgery
from app.models import Vaccination
from datetime import datetime

class MedicalCareService:
    
    # 알러지 기록
    @staticmethod
    def create_allergy(**kwargs):
        return Allergy.create(**kwargs)
    
    # 알러지 정보 목록
    @staticmethod
    def get_allergy_pet(pet_id: int):
        return Allergy.query.filter_by(pet_id=pet_id).all()
    
    # 질병 생성
    @staticmethod  
    def create_disease(**kwargs):
        return Disease.create(**kwargs)
    
    # 질병 정보 목록
    @staticmethod
    def get_disease_pet(pet_id: int):
        return Disease.query.filter_by(pet_id=pet_id).order_by(Disease.diagnosis_date.desc()).all()
    
    # 수술 이력 생성
    @staticmethod
    def create_surgery(**kwargs):
        return Surgery.create(**kwargs)
    
    # 수술 이력 정보 목록
    @staticmethod
    def get_surgery_pet(pet_id : int):
        return Surgery.query.filter_by(pet_id=pet_id).order_by(Surgery.surgery_date.desc()).all()

    # 예방 접종 생성
    @staticmethod
    def create_vaccination(**kwargs):
        return Vaccination.create(**kwargs)
    
    # 예방 접종 목록
    @staticmethod
    def get_vaccination_pet(pet_id: int):
        return Vaccination.query.filter_by(pet_id=pet_id).order_by(Vaccination.vaccination_date.desc()).all()
    
        
    @staticmethod
    def create_medication(**kwargs):
        return Medication.create(**kwargs)

    #약/영양제 조회
    @staticmethod
    def get_medications_by_pet(pet_id: int):
        return Medication.query.filter_by(pet_id=pet_id).order_by(Medication.created_at.desc()).all()

    @staticmethod
    def get_medication_by_id(medication_id: int):
        return Medication.query.get(medication_id)
