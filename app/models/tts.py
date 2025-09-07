from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.models.base import BaseModel
from app.models import db
from datetime import datetime

class TTSSettings(BaseModel):
    __tablename__ = 'tts_settings'
    
    id = Column(Integer, primary_key=True)
    pet_id = Column(String(36), ForeignKey('pets.pet_id'), nullable=False, unique=True)
    
    # TTS 제공업체 설정
    provider = Column(String(20), default='openai')  # 'openai' 또는 'gemini'
    is_enabled = Column(Boolean, default=True)
    
    # 음성 설정
    voice_id = Column(String(50), default='nova')  # OpenAI: nova, alloy, echo 등 / Gemini: Zephyr, Echo 등
    language_code = Column(String(10), default='ko')  # 언어 코드
    
    # 음성 파라미터
    speed = Column(Float, default=1.0)  # 속도 (0.25 ~ 4.0)
    pitch = Column(Float, default=0.0)  # 높낮이 (-20.0 ~ 20.0, OpenAI만 지원)
    volume = Column(Float, default=0.0)  # 볼륨 (-96.0 ~ 16.0, OpenAI만 지원)
    emotion = Column(Integer, default=0)  # 감정 (0=보통, 1=슬픔, 2=기쁨, 3=분노)
    
    # 메타 정보
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 관계 설정
    pet = relationship("Pet", back_populates="tts_settings")
    
    def to_dict(self):
        """TTS 설정을 딕셔너리로 변환"""
        return {
            'pet_id': self.pet_id,
            'provider': self.provider,
            'is_enabled': self.is_enabled,
            'voice_id': self.voice_id,
            'language_code': self.language_code,
            'speed': self.speed,
            'pitch': self.pitch,
            'volume': self.volume,
            'emotion': self.emotion,
            'pet_name': self.pet.pet_name if self.pet else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    @classmethod
    def get_by_pet_id(cls, pet_id):
        """펫 ID로 TTS 설정 조회"""
        return db.session.query(cls).filter(cls.pet_id == pet_id).first()
    
    @classmethod
    def create_default_settings(cls, pet_id, provider='openai'):
        """기본 TTS 설정 생성"""
        
        # 기존 설정이 있는지 확인
        existing = cls.get_by_pet_id(pet_id)
        if existing:
            return existing
        
        # 제공업체별 기본 설정
        default_voice = 'nova' if provider == 'openai' else 'Zephyr'
        
        settings = cls(
            pet_id=pet_id,
            provider=provider,
            voice_id=default_voice,
            is_enabled=True
        )
        
        db.session.add(settings)
        db.session.commit()
        return settings
    
    def update_settings(self, **kwargs):
        """TTS 설정 업데이트"""
        
        allowed_fields = [
            'provider', 'is_enabled', 'voice_id', 'language_code',
            'speed', 'pitch', 'volume', 'emotion'
        ]
        
        for field, value in kwargs.items():
            if field in allowed_fields:
                setattr(self, field, value)
        
        self.updated_at = datetime.utcnow()
        db.session.commit()
        return self

class TTSVoice(BaseModel):
    """사용 가능한 TTS 음성 목록"""
    __tablename__ = 'tts_voices'
    
    id = Column(Integer, primary_key=True)
    provider = Column(String(20), nullable=False)  # 'openai' 또는 'gemini'
    voice_id = Column(String(50), nullable=False)
    voice_name = Column(String(100), nullable=False)
    language_code = Column(String(10), nullable=False)
    gender = Column(String(10))  # 'male', 'female', 'neutral'
    category = Column(String(20))  # 'korean_female', 'korean_male', 'child_like', 'international'
    is_active = Column(Boolean, default=True)
    
    def to_dict(self):
        return {
            'provider': self.provider,
            'voice_id': self.voice_id,
            'voice_name': self.voice_name,
            'language_code': self.language_code,
            'gender': self.gender,
            'category': self.category,
            'is_active': self.is_active
        }
    
    @classmethod
    def get_voices_by_provider(cls, provider):
        """제공업체별 음성 목록 조회"""
        return db.session.query(cls).filter(
            cls.provider == provider,
            cls.is_active == True
        ).all()
    
    @classmethod
    def get_voices_by_category(cls, provider=None):
        """카테고리별로 그룹화된 음성 목록 조회"""
        
        query = db.session.query(cls).filter(cls.is_active == True)
        if provider:
            query = query.filter(cls.provider == provider)
        
        voices = query.all()
        
        # 카테고리별로 그룹화
        categorized = {}
        for voice in voices:
            category = voice.category or 'other'
            if category not in categorized:
                categorized[category] = {}
            categorized[category][voice.voice_id] = voice.voice_name
        
        return categorized