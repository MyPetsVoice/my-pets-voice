from app.models import db
from app.models.pet import Pet
from app.models.dailycare.healthCare.healthCare import HealthCare
from app.models.dailycare.healthCare.healthcareMedication import HealthCareMedication
from app.models.dailycare.healthCare.todo import TodoList
from app.models.dailycare.medicalCare.medication import Medication
from datetime import datetime, date, timedelta
from datetime import datetime, timedelta, timezone

    
class HealthCareService:
 
        @staticmethod
        def create_health_record(pet_id: int, **kwargs):
            """HealthCare 기록 생성 (BaseModel.create 활용), 하루에 한 개만 저장"""

            today = date.today()
            print(f'\n\n 오늘 시간은 ? : {today}')
            start_of_day = datetime.combine(today, datetime.min.time())
            end_of_day = datetime.combine(today, datetime.max.time())

            existing_record = HealthCare.query.filter_by(pet_id=pet_id).filter(
                HealthCare.created_at.between(start_of_day, end_of_day)
            ).first()

            if existing_record:
                print(f"[HealthCareService] 이미 오늘({today}) {pet_id}번 반려동물의 건강기록이 존재합니다.")
                return None

            return HealthCare.create(pet_id=pet_id, **kwargs)


        @staticmethod
        def get_health_records_by_pet(pet_id: int):
            """pet_id별 HealthCare 기록 조회"""
            return HealthCare.query.filter_by(pet_id=pet_id).order_by(HealthCare.created_at.desc()).all()

        @staticmethod
        def get_health_record_by_id(care_id: int):
            """특정 care_id 조회"""
            return HealthCare.query.get(care_id)

         

        
        @staticmethod
        def update_health_record(care_id: int, **kwargs):
            """특정 care_id 기록 갱신 + 연관 약물 처리"""
            record = HealthCare.query.get(care_id)
            if not record:
                return None

            # 문자열 datetime을 datetime 객체로 변환
            for key in ['updated_at', 'created_at']:
                if key in kwargs and isinstance(kwargs[key], str):
                    kwargs[key] = datetime.fromisoformat(kwargs[key])

            # HealthCare 필드 업데이트
            for key, value in kwargs.items():
                if hasattr(record, key) and key != 'medication_id':
                    setattr(record, key, value)

            # Medication 업데이트
            medication_id = kwargs.get('medication_id')
            if medication_id:
                med = HealthCareMedication.query.get(medication_id)
                if med:
                    med.record_id = record.care_id
                    med.updated_at = datetime.now()
                    db.session.add(med)

            db.session.commit()
            return record


        @staticmethod
        def delete_health_record(care_id: int):
            """특정 care_id 기록 삭제 + 연관 약물 처리"""
            record = HealthCare.query.get(care_id)
            if not record:
                return None

            # 연관된 Medication 처리: record_id 제거
            medications = HealthCareMedication.query.filter_by(record_id=record.care_id).all()
            for med in medications:
                db.session.delete(med)

            # HealthCare 삭제
            db.session.delete(record)
            db.session.commit()
            return True
    
        @staticmethod
        def link_medications(care_id, medication_ids):
            """헬스케어-약물 관계를 덮어쓰기 (기존 삭제 후 새로 추가)"""

            # 1. 기존 연결 삭제
            HealthCareMedication.query.filter_by(record_id=care_id).delete()

            # 2. 새 연결 삽입
            for med_id in medication_ids:
                HealthCareMedication.create(
                    record_id=care_id,
                    medication_id=med_id
                )

            db.session.commit()


        @staticmethod
        def get_linked_medications(care_id: int):
            links = HealthCareMedication.query.filter_by(record_id=care_id).all()
            return [link.medication for link in links]

                
        @staticmethod
        def create_todo_record(**kwargs):
            """TodoList 기록 생성 (BaseModel.create 활용)"""
            return TodoList.create(**kwargs)

        @staticmethod
        def get_todo_records_by_user_limit3(user_id: int):
            """pet_id별 TodoList 기록 조회"""
            
            result=TodoList.query.filter_by(user_id=user_id).order_by(TodoList.created_at.desc()).limit(3).all()
            print('\n\n result : ', result, ' userId : ', user_id)
            return result
        
        @staticmethod
        def get_todo_records_by_user(user_id: int):
            """pet_id별 TodoList 기록 조회"""
            return TodoList.query.filter_by(user_id=user_id).order_by(TodoList.created_at.desc()).all()
        
        
        @staticmethod
        def get_todo_record_by_id(todo_id: int, user_id: int = None):
            """특정 todo_id 조회, 필요 시 user_id 체크"""
            record = TodoList.query.get(todo_id)
            print(record)
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
                
            db.session.commit()
            return record
        
        @staticmethod
        def delete_todo_record(todo_id: int):
            """특정 todo_id 기록 삭제"""
            record = TodoList.query.get(todo_id)
            if not record:
                return None
            return record.delete()
        
        # 날짜로 건강기록 조회
        @staticmethod
        def get_health_records(pet_id, start_date, end_date):
            records = HealthCare.query.filter(
                HealthCare.pet_id == pet_id,
                HealthCare.created_at >= start_date,
                HealthCare.created_at <= end_date
            ).order_by(HealthCare.created_at.asc()).all()
            
            return records