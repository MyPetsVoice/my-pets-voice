from app.models import db
from app.models.base import BaseModel
from sqlalchemy import (
     Integer, String, Text, Date, ForeignKey, CheckConstraint, Index
)
from sqlalchemy.orm import relationship


class Surgery(BaseModel):
    """수술 이력 관리
    - 수술명, 날짜, 요약, 병원명, 회복 상태 기록
    """
    __tablename__ = 'surgeries'
    
    surgery_id = db.Column(Integer, primary_key=True, autoincrement=True)
    pet_id = db.Column(Integer, ForeignKey('pets.pet_id', ondelete='CASCADE'), nullable=False)
    
    surgery_name = db.Column(String(200), nullable=False)  # 수술명
    surgery_date = db.Column(Date, nullable=False)         # 수술일
    surgery_summary = db.Column(Text)                      # 수술 요약
    hospital_name = db.Column(String(200))                 # 
    doctor_name = db.Column(String(100))
    recovery_status = db.Column(String(20), nullable=False) # 회복 상태
    
    __table_args__ = (
        CheckConstraint(recovery_status.in_(['완전회복', '회복중', '경과관찰중']), name='check_recovery_status'),
        Index('idx_surgeries_pet_id', 'pet_id'),
    )
    
    pet = relationship("Pet", back_populates="surgeries")
    
    def __repr__(self):
        return f"<Surgery(id={self.surgery_id}, surgery='{self.surgery_name}')>"