from datetime import datetime
from app.models import db
from app.models.base import BaseModel

class Diary(BaseModel):
    __tablename__ = 'diary'

    diary_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    
    # 페르소나 직접 참조로 변경
    pet_persona_id = db.Column(db.Integer, db.ForeignKey('pet_personas.pet_persona_id', ondelete='CASCADE'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)

    diary_date = db.Column(db.Date, nullable=False, default=datetime.today)
    title = db.Column(db.String(200), nullable=False) 
    content_user = db.Column(db.Text)  # 사용자가 작성한 원본
    content_ai = db.Column(db.Text)  # AI가 변환한 반려동물 내용
    weather = db.Column(db.String(50))
    mood = db.Column(db.String(50))

    # 관계 설정
    user = db.relationship('User', backref=db.backref('diaries', lazy=True))
    # pet_persona 관계는 PetPersona 모델에서 정의됨 (cascade 적용)
    photos = db.relationship('DiaryPhoto', backref='diary', lazy=True, cascade='all, delete-orphan')

    def to_dict(self):
        result = super().to_dict()
        result.update({
            'diary_date': self.diary_date.isoformat() if self.diary_date else None,
            'photos': [photo.to_dict() for photo in self.photos],
        })
        return result

    #쿼리메소드
    @classmethod
    # 새 일기 생성
    def create_diary(cls, pet_persona_id, user_id, **kwargs):
        diary = cls(pet_persona_id=pet_persona_id, user_id=user_id, **kwargs)
        diary.save()
        return diary
    
    
    
    
    
    

class DiaryPhoto(BaseModel):
    __tablename__ = 'diary_photo'
    
    photo_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    diary_id = db.Column(db.Integer, db.ForeignKey('diary.diary_id', ondelete='CASCADE'), nullable=False)
    
    photo_url = db.Column(db.String(500), nullable=False)
    original_filename = db.Column(db.String(255))
    display_order = db.Column(db.Integer, default=0)

    def to_dict(self):
        result = super().to_dict()
        return result
    
    # 쿼리 메th드
    @classmethod
    # 새 일기 사진 생성
    def create_photo(cls, diary_id, **kwargs):
        photo = cls(diary_id=diary_id, **kwargs)
        photo.save()
        return photo
    