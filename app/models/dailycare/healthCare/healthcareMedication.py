from app.models import db
from app.models.base import BaseModel
from sqlalchemy import (
   Integer, ForeignKey, 
)
from sqlalchemy.orm import relationship
from dotenv import load_dotenv
load_dotenv()
class HealthCareMedication(BaseModel):
    """건강 기록에 포함된 약물 기록
    중간테이블
    - 특정 HealthCare 기록에서 복용한 Medication을 연결
    - 예: 오늘(HealthCare) → 처방약 A, 보조제 B (Medication) 기록
    """
    __tablename__ = 'healthcare_medications'

    id = db.Column(Integer, primary_key=True, autoincrement=True)

    # HealthCare 기록
    record_id = db.Column(
        Integer, 
        ForeignKey('health_cares.care_id', ondelete="CASCADE"), 
        nullable=False
    )

    # Medication 참조
    medication_id = db.Column(
        Integer, 
        ForeignKey('medications.medication_id', ondelete="CASCADE"), 
        nullable=False
    )

    # 관계 설정
    healthcare = relationship("HealthCare", backref="medication_links")
    medication = relationship("Medication", backref="healthcare_links")