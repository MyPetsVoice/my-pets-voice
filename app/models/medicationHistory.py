from app.models import db
from app.models.base import BaseModel
from sqlalchemy import (
    Column, Integer, String, Text, Date, DateTime, Decimal, Boolean, 
    Time, ForeignKey, CheckConstraint, UniqueConstraint, Index
)
from sqlalchemy.orm import relationship

 # -----------Allergy-----------    
class Allergy(BaseModel):
    """데일리케어 > 의료기록 > 알러지 정보"""
    __tablename__ = 'allergies'
    
    allergy_id = db.Column(Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(Integer, ForeignKey('user.user_id', ondelete='CASCADE'), nullable=False)
    #알러지타입 / 음식, 접촉, 환경, 약물, 기타
    allergy_type = db.Column(String(20), nullable=False)
    # 알러지원 / 음식 > 사과
    allergen = db.Column(String(200), nullable=False)
    # 증상
    symptoms = db.Column(String)
    # 심각도 / 경미 / 보통 / 심각
    severity = db.Column(String(20), nullable=False)
    
    # 제약조건
    __table_args__ = (
        CheckConstraint(
            allergy_type.in_(['음식', '접촉', '환경', '약물', '기타']),
            name='check_allergy_type'
        ),
        CheckConstraint(
            severity.in_(['경미', '보통', '심각']),
            name='check_severity'
        ),
        Index('idx_allergies_user_id', 'user_id'),
    )
    
    # 관계 설정
    user = relationship("User", back_populates="allergies")
    
    def __repr__(self):
        return f"<Allergy(id={self.allergy_id}, type='{self.allergy_type}', allergen='{self.allergen}')>"

# -----------Disease----------- 
class Disease(BaseModel):
    """데일리케어 > 의료기록 > 질병 이력"""
    __tablename__ = 'disease'
    
    disease_id = db.Column(Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(Integer, ForeignKey('user.user_id', ondelete='CASCADE'), nullable=False)
    # 질병 이름
    disease_name = db.Column(String(200), nullable=False)
    #증상
    symptoms = db.Column(Text)
    # 치료 세부사항 
    treatment_details = db.Column(Text)
    # 병원 이름
    hospital_name = db.Column(String(200))
    # 비용
    medical_cost = db.Column(Decimal(10, 2))
    # 진단일
    diagnosis_date = db.Column(Date)
    
    __table_args__ = (
        Index('idx_disease_user_id', 'user_id'),
    )
    
    # 관계 설정
    user = relationship("User", back_populates="disease")
    
    def __repr__(self):
        return f"<DiseaseHistory(id={self.disease_id}, disease='{self.disease_name}')>"
    
# -----------Surgery-----------     
class Surgery(BaseModel):
    __tablename__ = 'surgeries'
    """데일리케어 > 의료기록 > 수술 이력"""
  
    
    surgery_id = db.Column(Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(Integer, ForeignKey('users.user_id', ondelete='CASCADE'), nullable=False)
    surgery_name = db.Column(String(200), nullable=False)
    surgery_date = db.Column(Date, nullable=False)
    surgery_summary = db.Column(Text)
    hospital_name = db.Column(String(200))
    #회복 상태
    recovery_status = db.Column(String(20), nullable=False)
    
    __table_args__ = (
        CheckConstraint(
            recovery_status.in_(['완전회복', '회복중', '경과관찰중']),
            name='check_recovery_status'
        ),
        Index('idx_surgery_history_user_id', 'user_id'),
    )
    
    # 관계 설정
    user = relationship("User", back_populates="surgeries")
    
    def __repr__(self):
        return f"<Surgeries(id={self.surgery_id}, surgery='{self.surgery_name}')>"
# -----------Vaccination-----------   
class Vaccination(BaseModel):
    """데일리케어 > 의료기록 > 예방접종"""
    __tablename__ = 'vaccinations'
    
    vaccination_id = db.Column(Integer, primary_key=True, autoincrement=True)
    member_id = db.Column(Integer, ForeignKey('members.member_id', ondelete='CASCADE'), nullable=False)
    vaccine_name = db.Column(String(200), nullable=False)
    vaccination_date = db.Column(Date, nullable=False)
    # 부작용
    side_effects = db.Column(Text)
    hospital_name = db.Column(String(200))
    #다음검진일
    next_vaccination_date = db.Column(Date)
    
    __table_args__ = (
        Index('idx_vaccinations_user_id', 'user_id'),
    )
    
    # 관계 설정
    user = relationship("User", back_populates="vaccinations")
    
    def __repr__(self):
        return f"<Vaccination(id={self.vaccination_id}, vaccine='{self.vaccine_name}')>"
# -----------Medication-----------     
class Medication(BaseModel):
    """데일리케어 > 의료기록 > 복용약물 관리"""
    __tablename__ = 'medications'
    
    medication_id = db.Column(Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(Integer, ForeignKey('users.user_id', ondelete='CASCADE'), nullable=False)
    
    medication_name = db.Column(String(200), nullable=False)
    #복용목적
    purpose = db.Column(String(500))
    #용량
    dosage = db.Column(String(100))
    #횟수 / 하루 1회 /2회/3회/필요시
    frequency = db.Column(String(20), nullable=False)
    #복용시작일
    start_date = db.Column(Date)
    #복용종료
    end_date = db.Column(Date)
    #부작용
    side_effects_notes = db.Column(Text)
    #병원이름
    hospital_name = db.Column(String(200))
    
    __table_args__ = (
        CheckConstraint(
            frequency.in_(['하루1회', '하루2회', '하루3회', '필요시']),
            name='check_frequency'
        ),
        Index('idx_medications_user_id', 'user_id'),
    )
    
    # 관계 설정
    member = relationship("User", back_populates="medications")
    daily_medication_logs = relationship("DailyMedicationLog", back_populates="medication", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Medication(id={self.medication_id}, name='{self.medication_name}')>"

#의료기록 모아보기는 따로 만들어야 함!
