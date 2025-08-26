from app.models import db
from app.models.base import BaseModel
from sqlalchemy import (
  Integer, String, Text, Date, ForeignKey, CheckConstraint, Index
)
from sqlalchemy.orm import relationship

# ==========================
#  ✅ 할 일 관리 (Todo List)
# ==========================

class TodoList(BaseModel):
    """Todo 리스트
    - 하루 단위 할 일 관리 (제목, 설명, 상태, 우선순위)
    """
    __tablename__ = 'todos'
    
    todo_id = db.Column(Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(Integer, ForeignKey('users.user_id', ondelete='CASCADE'), nullable=False)
    
    todo_date = db.Column(Date, nullable=False)           # 해당 날짜
    title = db.Column(String(200), nullable=False)        # 제목
    description = db.Column(Text)                         # 세부 내용
    status = db.Column(String(20), default='미완료')      # 상태
    priority = db.Column(String(20), default='보통')      # 우선순위
    
    __table_args__ = (
        CheckConstraint(status.in_(['미완료', '완료']), name='check_status'),
        CheckConstraint(priority.in_(['낮음', '보통', '높음']), name='check_priority'),
        Index('idx_todo_lists_user_date', 'user_id', 'todo_date'),
    )
    
    user = relationship("User", back_populates="todos")
    
    def __repr__(self):
        return f"<TodoList(id={self.todo_id}, title='{self.title}', status='{self.status}')>"