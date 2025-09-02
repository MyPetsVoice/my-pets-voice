from app.models import db
from app.models.base import BaseModel
from sqlalchemy import (
     Integer, String, Text, Date, ForeignKey, CheckConstraint, Index
)
from sqlalchemy.orm import relationship

class Medication(BaseModel):
    """복용 약물 관리
    - 현재/과거 복용 중인 약물 등록
    - 복용 목적, 용량, 횟수, 복용 기간, 부작용 기록
    """
    __tablename__ = 'medications'
    
    medication_id = db.Column(Integer, primary_key=True, autoincrement=True)
    pet_id = db.Column(Integer, ForeignKey('pets.pet_id', ondelete='CASCADE'), nullable=False)
    
    medication_name = db.Column(String(200), nullable=False)  # 약물명
    purpose = db.Column(String(500))                          # 복용 목적
    dosage = db.Column(String(100))                           # 용량
    frequency = db.Column(String(20), nullable=False)         # 복용 횟수
    start_date = db.Column(Date)
    end_date = db.Column(Date)                                # 복용 종료일
    side_effects_notes = db.Column(Text)                      # 부작용 기록
    hospital_name = db.Column(String(200))                    # 병원명
    
    __table_args__ = (
        CheckConstraint("frequency IN ('하루1회', '하루2회', '하루3회', '필요시')", name='check_frequency'),
        Index('idx_medications_pet_id', 'pet_id'),
    )
    
    pet = relationship("Pet", back_populates="medications")
    health_cares = db.relationship('HealthCare', back_populates='medication')
   
    def __repr__(self):
        return f"<Medication(id={self.medication_id}, name='{self.medication_name}')>"