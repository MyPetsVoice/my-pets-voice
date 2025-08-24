from app.models import db
from app.models.pet import Pet
from app.models.dailycare.healthCare.healthCare import HealthCare
from app.models.dailycare.healthCare.healthcareMedication import HealthCareMedication
from app.models.dailycare.medicalCare.medication import Medication

from datetime import datetime

    
class HealthCareService:
 
        @staticmethod
        def create_health_record(**kwargs):
            """HealthCare 기록 생성 (BaseModel.create 활용)"""
            return HealthCare.create(**kwargs)

        @staticmethod
        def get_health_records_by_pet(pet_id: int):
            """pet_id별 HealthCare 기록 조회"""
            return HealthCare.query.filter_by(pet_id=pet_id).order_by(HealthCare.created_at.desc()).all()

        @staticmethod
        def get_health_record_by_id(care_id: int, pet_id: int = None):
            """특정 care_id 조회, 필요 시 pet_id 체크"""
            record = HealthCare.query.get(care_id)
            if not record:
                return None
            if pet_id is not None and record.pet_id != pet_id:
                return None
            return record
        @staticmethod
        def link_medications(care_id, medication_ids):
            for med_id in medication_ids:
                HealthCareMedication.create(
                record_id=care_id,
                medication_id=med_id
            )
