from app.models import db
from app.models.base import BaseModel
from app.models.pet import Pet
from sqlalchemy import (
     Integer, String, ForeignKey, CheckConstraint, Index
)
from sqlalchemy.orm import relationship

class Allergy(BaseModel):
    """알러지 정보 관리
    - 음식, 접촉, 환경, 약물, 기타 유형별 알러지 기록
    - 알러지원(예: 사과, 꽃가루 등), 증상, 심각도 저장
    """
    __tablename__ = 'allergies'
    
    allergy_id = db.Column(Integer, primary_key=True, autoincrement=True)
    pet_id = db.Column(Integer, ForeignKey('pets.pet_id', ondelete='CASCADE'), nullable=False)
    allergy_type = db.Column(String(20), nullable=False)   # 알러지 유형
    allergen = db.Column(String(200), nullable=False)      # 알러지원
    symptoms = db.Column(String)                           # 증상
    severity = db.Column(String(20), nullable=False)       # 심각도
    
    __table_args__ = (
        CheckConstraint(allergy_type.in_(['음식', '접촉', '환경', '약물', '기타']), name='check_allergy_type'),
        CheckConstraint(severity.in_(['경미', '보통', '심각']), name='check_severity'),
        Index('idx_allergies_pet_id', 'pet_id'),
    )
    
    pet = relationship("Pet", back_populates="allergies")
    
    def __repr__(self):
        return f"<Allergy(id={self.allergy_id}, type='{self.allergy_type}', allergen='{self.allergen}')>"