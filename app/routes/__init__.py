# 모든 라우트 블루프린트 중앙 관리
from app.routes.auth import auth_bp
from app.routes.chat import chat_bp
from app.routes.dailycare import dailycare_bp
from app.routes.diary import diary_bp
from app.routes.mypage import mypage_bp
from app.routes.weather import weather_bp


def register_blueprints(app):
    """모든 블루프린트를 Flask 앱에 등록"""
    app.register_blueprint(auth_bp)
    app.register_blueprint(chat_bp)
    app.register_blueprint(dailycare_bp)
    app.register_blueprint(diary_bp)
    app.register_blueprint(mypage_bp)
    app.register_blueprint(weather_bp)
    
    
    

__all__ = [
    'auth_bp', 
    'chat_bp', 
    'dailycare_bp', 
    'diary_bp', 
    'mypage_bp',
    'register_blueprints',
    'weather_bp'
]