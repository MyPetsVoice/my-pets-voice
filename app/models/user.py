from datetime import datetime
from app.models import db
from app.models.base import BaseModel, get_utc_now

class User(BaseModel):
    __tablename__ = 'users'

    user_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    nickname = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    profile_img_url = db.Column(db.String(500))
    authority = db.Column(db.String(20), default='user', nullable=False)
    social_provider = db.Column(db.String(100))
    social_id = db.Column(db.String(100))
    last_login_at = db.Column(db.DateTime(timezone=True))
    
    todos = db.relationship("TodoList", back_populates="user", lazy=True)

    def __repr__(self):
        return f'<User {self.username}>'
    
    @classmethod
    def create_user(cls, **kwargs):
        user = cls(**kwargs)
        db.session.add(user)
        db.session.commit()
        return user

    @classmethod
    def create_user_from_kakao(cls, user):
        username = f'kakao_{user["id"]}'
        profile = user['kakao_account']['profile']
        kakao_account = user['kakao_account']

        return cls.create_user(
            username=username,
            nickname=profile.get('nickname','사용자'),
            email=kakao_account.get('email'),
            profile_img_url=profile.get('profile_image_url'),
            social_provider='kakao',
            social_id=str(user['id']),
            last_login_at=get_utc_now()
        )
    
#     @classmethod
# def create_from_kakao(cls, kakao_user_info):
#     """카카오 정보로 사용자 생성"""
#     try:
#         # 필수 정보
#         kakao_id = kakao_user_info['id']
#         username = f"kakao_{kakao_id}"
        
#         # 선택적 정보 (없을 수도 있으므로 안전하게 처리)
#         kakao_account = kakao_user_info.get('kakao_account', {})
#         profile = kakao_account.get('profile', {})
        
#         # 닉네임 우선순위: profile.nickname > properties.nickname > 기본값
#         nickname = (
#             profile.get('nickname') or 
#             kakao_user_info.get('properties', {}).get('nickname') or 
#             '사용자'
#         )
        
#         return cls.create_user(
#             username=username,
#             nickname=nickname,
#             email=kakao_account.get('email'),
#             profile_img_url=profile.get('profile_image_url'),
#             social_provider='kakao',
#             social_id=str(kakao_id),
#             last_login_at=datetime.now()
#         )
        
#     except KeyError as e:
#         raise ValueError(f"카카오 사용자 정보에 필수 필드가 없습니다: {e}")
        


    @classmethod
    def find_by_social(cls, provider, social_id):
        user = cls.query.filter_by(social_provider=provider, social_id=social_id).first()
        return user
    


    def update_last_login(self):
        self.last_login_at = get_utc_now()
        db.session.commit()