from app.models import db, Pet
from app.models.dailycare.medicalCare.medication import Medication
from datetime import datetime

class MedicationService:

    @staticmethod
    def create_medication(**kwargs):
        """Medication 기록 생성 (BaseModel.create 활용)"""
        return Medication.create(**kwargs)

    @staticmethod
    def get_medications_by_pet(pet_id: int):
        """pet_id별 약/영양제 조회"""
        return Medication.query.filter_by(pet_id=pet_id).order_by(Medication.created_at.desc()).all()

    @staticmethod
    def get_medication_by_id(medication_id: int):
        """특정 약 조회"""
        return Medication.query.get(medication_id)
