from app.models import db
from app.models.pet import Pet
from app.models.dailycare.healthCare.healthCare import HealthCare
from app.models.dailycare.healthCare.healthcareMedication import HealthCareMedication
from app.models.dailycare.healthCare.todo import TodoList
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
                
        @staticmethod
        def create_todo_record(**kwargs):
            """TodoList 기록 생성 (BaseModel.create 활용)"""
            return TodoList.create(**kwargs)

        @staticmethod
        def get_todo_records_by_user_limit3(user_id: int):
            """pet_id별 TodoList 기록 조회"""
            return TodoList.query.filter_by(user_id=user_id).order_by(TodoList.created_at.desc()).limit(3).all()
        @staticmethod
        def get_todo_records_by_user(user_id: int):
            """pet_id별 TodoList 기록 조회"""
            return TodoList.query.filter_by(user_id=user_id).order_by(TodoList.created_at.desc()).all()
        
        
        @staticmethod
        def get_todo_record_by_id(todo_id: int, user_id: int = None):
            """특정 todo_id 조회, 필요 시 pet_id 체크"""
            record = TodoList.query.get(todo_id)
            if not record:
                return None
            if user_id is not None and record.user_id != user_id:
                return None
            return record 
        
        @staticmethod
        def update_todo_record(todo_id: int, **kwargs):
            """특정 todo_id 기록 갱신"""
            record = TodoList.query.get(todo_id)
            if not record:
                return None
            for key, value in kwargs.items():
                setattr(record, key, value)
            return record.save  
        @staticmethod
        def delete_todo_record(todo_id: int):
            """특정 todo_id 기록 삭제"""
            record = TodoList.query.get(todo_id)
            if not record:
                return None
            return record.delete()
