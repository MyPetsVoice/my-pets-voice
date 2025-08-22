from app.models import db
from app.models.base import BaseModel
from sqlalchemy import (
    Column, Integer, String, Text, Date, DateTime, Decimal, Boolean, 
    Time, ForeignKey, CheckConstraint, UniqueConstraint, Index
)
from sqlalchemy.orm import relationship
#----------------HealthCare----------------------
class HealthCare(BaseModel):
    """건강기록 
     데일리 케어 > 건강기록입니다. 
    """
    __tablename__ = 'health_cares'
    
    care_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, ForeignKey('users.user_id', ondelete='CASCADE'), nullable=False)
    # 음식 섭취량: 먹음 / 조금먹음 / 안먹음
    food = db.Column(String(20))
    
    # 물 섭취량
    water = db.Column(db.DECIMAL(6, 2))
    
    # 대변 상태: 정상 / 설사 / 변비 / 혈변
    excrement_status = db.Column(String(20))
    
    # 몸무게
    weight_kg = db.Column(db.DECIMAL(5, 2))
    
    # 산책시간 (분)
    walk_time_minutes = db.Column(Integer)

    __table_args__ = (
        CheckConstraint(
            food.in_(['먹음', '조금먹음', '안먹음']),
            name='check_food_intake'
        ),
        CheckConstraint(
            excrement_status.in_(['정상', '설사', '변비', '혈변']),
            name='check_bowel_status'
        ),
        UniqueConstraint('user_id', 'created_at', name='uq_user_record_date'),
        Index('idx_health_records_user_date', 'user_id', 'created_at'),
    )
    
    
    user = relationship("User", backref="health_records")
    daily_medication_logs = relationship(
        #DailyMedication Model과 정의할 것임
        "DailyMedicationLog",
        # daily_record라는 속성명으로 명시적으로 관계를 정의 해야함.
        back_populates="daily_record",
        # 부모 객체가 삭제되면 관련된 자식객체도 삭제, 부모가 없는 객체가 존재한다면 그것도 삭제
        cascade="all, delete-orphan"
    )
    
    def __repr__(self):
        return f"<HealthCare(id={self.care_id}, created_at='{self.created_at}')>"
# -----------HealthCareLog-----------

class HealthCareLog(BaseModel):
    """데일리케어 > 건강기록 > 건강기록 기록 모아보기"""
    __tablename__ = 'daily_medication_logs'
    
    # 기록 id
    log_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    
    # HealthCare.care_id
    record_id = db.Column(db.Integer, ForeignKey('health_cares.care_id', ondelete='CASCADE'), nullable=False)
    
    # Medication.medication_id
    medication_id = db.Column(db.Integer, ForeignKey('medications.medication_id', ondelete='CASCADE'), nullable=False)
    
    # 관계 설정
    daily_record = relationship("HealthCare", back_populates="daily_medication_logs")
    medication = relationship("Medication", back_populates="daily_medication_logs")
    
    def __repr__(self):
        return f"<HealthCareLog(id={self.log_id}, record_id={self.record_id}, medication_id={self.medication_id})>"
    
    
 # -----------TODOLIST-----------   
class TodoList(BaseModel):
    """데일리케어 > 날짜별 Todo 리스트"""
    __tablename__ = 'todos'
    
    todo_id = db.Column(Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(Integer, ForeignKey('users.user_id', ondelete='CASCADE'), nullable=False)
    todo_date = db.Column(Date, nullable=False)
    # 제목
    title = db.Column(String(200), nullable=False)
    # 세부내용
    description = db.Column(Text)
    #상태 미완료 / 완료
    status = db.Column(String(20), default='미완료')
    #우선순위 낮음 / 보통 / 높음
    priority = db.Column(String(20), default='보통')
    #제약사항
    __table_args__ = (
        CheckConstraint(
            status.in_(['미완료', '완료']),
            name='check_status'
        ),
        CheckConstraint(
            priority.in_(['낮음', '보통', '높음']),
            name='check_priority'
        ),
        Index('idx_todo_lists_user_date', 'user_id', 'todo_date'),
    )
    
    # 관계 설정
    user = relationship("User", back_populates="todos")
    
    def __repr__(self):
        return f"<TodoList(id={self.todo_id}, title='{self.title}', status='{self.status}')>"
    
