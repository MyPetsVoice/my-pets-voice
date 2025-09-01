import os
import logging
from dotenv import load_dotenv

load_dotenv()

class Config:
    # 세션 설정
    SECRET_KEY = os.getenv('SESSION_SECRET_KEY', 'your-secret-key-here')
    
    # 데이터베이스 설정
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///mypetsvoice-xuswns.db')
    print('연결된 database : ',SQLALCHEMY_DATABASE_URI)

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # OpenAI API 설정
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    
    # 카카오 로그인 설정
    KAKAO_REST_API_KEY = os.getenv('KAKAO_REST_API_KEY')
    KAKAO_CLIENT_SECRET = os.getenv('KAKAO_CLIENT_SECRET')
    KAKAO_REDIRECT_URI = os.getenv('KAKAO_REDIRECT_URI')

    KAPI_HOST = "https://kapi.kakao.com"
    KAUTH_HOST = "https://kauth.kakao.com"
    
    # 로깅 모듈 설정
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    LOG_FILE = os.getenv('LOG_FILE', 'logs/app.log')
    
    # 디버깅 모드
    DEBUG = os.getenv('DEBUG', 'True').lower() == 'true'

class DevelopmentConfig(Config):
    DEBUG = True
    LOG_LEVEL = 'DEBUG'

class ProductionConfig(Config):
    DEBUG = False
    LOG_LEVEL = 'WARNING'

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}

def setup_logging(app):
    # 로그 파일 저장
    if not os.path.exists('logs'):
        os.makedirs('logs')
    
    # 로그 레벨 설정
    log_level = getattr(logging, app.config['LOG_LEVEL'].upper(), logging.INFO)
    
    # 파일 핸들러
    file_handler = logging.FileHandler(app.config['LOG_FILE'], encoding='utf-8')
    file_handler.setLevel(log_level)
    file_handler.setFormatter(logging.Formatter(app.config['LOG_FORMAT']))
    
    # 콘솔 핸들러 설정
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    console_handler.setFormatter(logging.Formatter(app.config['LOG_FORMAT']))
    
    # Flask 앱 logger 설정
    app.logger.setLevel(log_level)
    app.logger.addHandler(file_handler)
    app.logger.addHandler(console_handler)
    
    # Werkzeug 로거 레벨 조정 (개발 환경에서 너무 많은 로그 방지)
    if not app.config['DEBUG']:
        logging.getLogger('werkzeug').setLevel(logging.WARNING)
    
    app.logger.info('로깅 설정 완료')