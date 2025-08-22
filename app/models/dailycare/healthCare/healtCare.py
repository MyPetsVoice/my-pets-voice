from app.models import db
from app.models.base import BaseModel
from sqlalchemy import (
    Integer, String, ForeignKey, CheckConstraint, UniqueConstraint, Index, DECIMAL
)
from sqlalchemy.orm import relationship

# ==========================
#  🩺 건강 기록 (Health Care)
# ==========================

class HealthCare(BaseModel):
    """일상 건강 기록
    - 하루 단위 식사, 수분 섭취, 배변 상태, 몸무게, 산책시간 기록
    """
    __tablename__ = 'health_cares'
    
    care_id = db.Column(Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(Integer, ForeignKey('users.user_id', ondelete='CASCADE'), nullable=False)
    
    food = db.Column(Integer)                  # 음식 섭취량
    water = db.Column(DECIMAL(6, 2))           # 수분 섭취량 (ml)
    excrement_status = db.Column(String(20))   # 배변 상태
    weight_kg = db.Column(DECIMAL(5, 2))       # 몸무게 (kg)
    walk_time_minutes = db.Column(Integer)     # 산책시간 (분)
    
    __table_args__ = (
        CheckConstraint(excrement_status.in_(['정상', '설사', '변비', '혈변']), name='check_bowel_status'),
        UniqueConstraint('user_id', 'created_at', name='uq_user_record_date'),
        Index('idx_health_records_user_date', 'user_id', 'created_at'),
    )
    
    user = relationship("User", backref="health_records")
    daily_medication_logs = relationship(
        "HealthCareLog",
        back_populates="daily_record",
        cascade="all, delete-orphan"
    )
    
    def __repr__(self):
        return f"<HealthCare(id={self.care_id}, created_at='{self.created_at}')>"


