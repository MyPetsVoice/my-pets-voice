from app.models import db
from app.models.base import BaseModel
from sqlalchemy import (
     Integer, String, Text, Date, ForeignKey, Index
)
from sqlalchemy.orm import relationship

class Vaccination(BaseModel):
    """예방접종 기록
    - 백신명, 접종일, 부작용, 병원명, 다음 접종 예정일 기록
    """
    __tablename__ = 'vaccinations'
    
    vaccination_id = db.Column(Integer, primary_key=True, autoincrement=True)
    pet_id = db.Column(Integer, ForeignKey('pets.pet_id', ondelete='CASCADE'), nullable=False)
    
    vaccine_name = db.Column(String(200), nullable=False)   # 백신명
    vaccination_date = db.Column(Date, nullable=False)      # 접종일
    side_effects = db.Column(Text)                          # 부작용
    hospital_name = db.Column(String(200))                  # 병원명
    next_vaccination_date = db.Column(Date)                 # 다음 접종 예정일
    manufacturer = db.Column(String(200))  # 제조회사 추가
    lot_number = db.Column(String(100))    # 로트번호 추가
    
    __table_args__ = (
        Index('idx_vaccinations_pet_id', 'pet_id'),
    )
    
    pet = relationship("Pet", back_populates="vaccinations")
    
    def __repr__(self):
        return f"<Vaccination(id={self.vaccination_id}, vaccine='{self.vaccine_name}')>"