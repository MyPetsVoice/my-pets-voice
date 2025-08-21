from datetime import datetime
from app.models import db

class Diary(db.Model):
    
    __tablename__ = 'diary'

    diary_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    pet_id = db.Column(db.Integer, nullable=False, default=1)  # 임시
    user_id = db.Column(db.Integer, nullable=False, default=1)  # 임시

    diary_date = db.Column(db.Date, nullable=False, default=datetime.today)  # 일기 날짜
    title = db.Column(db.String(200), nullable=False) 
    content_user = db.Column(db.Text)  # 사용자가 작성한 원본
    content_ai = db.Column(db.Text)  # AI가 변환한 반려동물 내용
    weather = db.Column(db.String(50))  # 날씨
    mood = db.Column(db.String(50))  # 기분

    created_at = db.Column(db.DateTime, default=datetime.now)  # 생성 시간
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now) # 뺄 생각

    photos = db.relationship('DiaryPhoto', backref='diary', lazy=True, cascade='all, delete-orphan')

def to_dict(self):
    """
    JSON 응답을 위해 딕셔너리로 변환
    """
    return {
        'diary_id': self.diary_id,
        'pet_id': self.pet_id,
        'user_id': self.user_id,
        'diary_date': self.diary_date.isoformat() if self.diary_date else None,
        'title': self.title,
        'content_user': self.content_user,
        'content_ai': self.content_ai,
        'weather': self.weather,
        'mood': self.mood,
        'photos': [photo.to_dict() for photo in self.photos],  
        'created_at': self.created_at.isoformat() if self.created_at else None,
        'updated_at': self.updated_at.isoformat() if self.updated_at else None
    }
        
class DiaryPhoto(db.Model):
    
    __tablename__ = 'diary_photo'
    
    photo_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    
    # (어느 일기의 사진인지)
    diary_id = db.Column(db.Integer, db.ForeignKey('diary.diary_id'), nullable=False)
    
    # 사진 정보
    photo_url = db.Column(db.String(500), nullable=False)  # 사진 파일 경로나 URL
    original_filename = db.Column(db.String(255))  # 원본 파일명
    display_order = db.Column(db.Integer, default=0)  # 표시 순서
    
    # 생성 시간
    created_at = db.Column(db.DateTime, default=datetime.now)
    
def to_dict(self):
    """딕셔너리로 변환"""
    return {
        'photo_id': self.photo_id,
        'diary_id': self.diary_id,
        'photo_url': self.photo_url,
        'original_filename': self.original_filename,
        'display_order': self.display_order,
        'created_at': self.created_at.isoformat() if self.created_at else None
    }
    