from app.models import db
from app.models.base import BaseModel
from sqlalchemy import (
     Integer, String, ForeignKey, Index, Text, DECIMAL, Date
)
from sqlalchemy.orm import relationship

class Disease(BaseModel):
    """질병 이력 관리
    - 과거/현재 질병명, 증상, 치료 내역, 병원명, 담당 의사, 비용, 진단일 기록
    """
    __tablename__ = 'diseases'
    
    disease_id = db.Column(Integer, primary_key=True, autoincrement=True)
    pet_id = db.Column(Integer, ForeignKey('pets.pet_id', ondelete='CASCADE'), nullable=False)
    disease_name = db.Column(String(200), nullable=False)  # 질병 이름
    symptoms = db.Column(Text)                             # 증상
    treatment_details = db.Column(Text)                    # 치료 내역
    hospital_name = db.Column(String(200))                 # 병원명
    doctor_name = db.Column(String(100))                   # 담당 의사명
    medical_cost = db.Column(DECIMAL(10, 2))               # 진료비
    diagnosis_date = db.Column(Date)                       # 진단일
    
    __table_args__ = (
        Index('idx_diseases_pet_id', 'pet_id'),
    )
    
    pet = relationship("Pet", back_populates="diseases")
    
    def __repr__(self):
        return f"<Disease(id={self.disease_id}, disease='{self.disease_name}')>"