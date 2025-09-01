# 모든 라우트 블루프린트 중앙 관리
from app.routes.auth import auth_bp
from app.routes.chat import chat_bp
from app.routes.dailycare import dailycare_bp
from app.routes.diary import diary_bp
from app.routes.mypage import mypage_bp

# API 별도 블루프린트들 (chat과 dailycare는 이미 메인 bp에 포함됨)
from app.routes.diary.diary_api import diary_api_bp

def register_blueprints(app):
    """모든 블루프린트를 Flask 앱에 등록"""
    app.register_blueprint(auth_bp)
    app.register_blueprint(chat_bp)
    app.register_blueprint(dailycare_bp)
    app.register_blueprint(diary_bp)
    app.register_blueprint(mypage_bp)
    

__all__ = [
    'auth_bp', 
    'chat_bp', 
    'dailycare_bp', 
    'diary_bp', 
    'mypage_bp',
    'diary_api_bp',
    'register_blueprints'
]