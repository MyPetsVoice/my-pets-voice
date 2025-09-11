import os
import logging
from dotenv import load_dotenv

load_dotenv()

class Config:
    # 세션 설정
    SECRET_KEY = os.getenv('SESSION_SECRET_KEY')
    
    # 데이터베이스 설정
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')
    print('연결된 database : ',SQLALCHEMY_DATABASE_URI)

    # SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # 벡터DB 설정
    VECTOR_DB = os.getenv('VECTOR_DB', './vector_db')
    DOCUMENTS_PATH = os.getenv('DOCUMENTS_PATH')

    # 파일 저장 경로
    STORAGE_PATH=os.getenv('STORAGE_PATH', os.path.join(os.path.dirname(__file__), 'app', 'static', 'uploads'))

    # OpenAI API 설정
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    
    # 카카오 로그인 설정
    KAKAO_REST_API_KEY = os.getenv('KAKAO_REST_API_KEY')
    KAKAO_CLIENT_SECRET = os.getenv('KAKAO_CLIENT_SECRET')
    KAKAO_REDIRECT_URI = os.getenv('KAKAO_REDIRECT_URI')
    KAKAO_LOGOUT_REDIRECT_URI = os.getenv('KAKAO_LOGOUT_REDIRECT_URI')
    KAPI_HOST = os.getenv('KAPI_HOST')
    KAUTH_HOST = os.getenv('KAUTH_HOST')
    
    # LangSmith 설정
    LANGCHAIN_API_KEY = os.getenv('LANGCHAIN_API_KEY')
    LANGSMITH_PROJECT = os.getenv('LANGSMITH_PROJECT')
    LANGSMITH_ENDPOINT = os.getenv('LANGSMITH_ENDPOINT', 'https://api.smith.langchain.com')
    LANGSMITH_TRACING = os.getenv('LANGSMITH_TRACING', 'true').lower() == 'true'
    
    # 로깅 모듈 설정
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    LOG_FILE = os.getenv('LOG_FILE', 'logs/app.log')
    
    # 디버깅 모드
    DEBUG = os.getenv('DEBUG', 'True').lower() == 'true'

    @classmethod
    def validate(cls):
        # 필수 값 있는지 확인
        required_vars = {
            'SESSION_SECRET_KEY': cls.SECRET_KEY,
            'DATABASE_URL': cls.SQLALCHEMY_DATABASE_URI,
            'OPENAI_API_KEY': cls.OPENAI_API_KEY,
            'KAKAO_REST_API_KEY': cls.KAKAO_REST_API_KEY,
            'KAKAO_CLIENT_SECRET': cls.KAKAO_CLIENT_SECRET,
            'KAKAO_REDIRECT_URI': cls.KAKAO_REDIRECT_URI
        }
        missing = [key for key, value in required_vars.items() if not value]
        if missing:
            raise ValueError(f"필수 환경변수가 설정되지 않았습니다.: {', '.join(missing)}")


class DevelopmentConfig(Config):
    DEBUG = True
    LOG_LEVEL = 'DEBUG'

class ProductionConfig(Config):
    DEBUG = False
    LOG_LEVEL = 'DEBUG'

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}

def setup_logging(app):
    # 기존 핸들러 제거 (중복 방지)
    if app.logger.handlers:
        app.logger.handlers.clear()
    
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
    
    # 상위 로거로 전파 방지 (중복 로그 방지)
    app.logger.propagate = False
    
    # Werkzeug 로거 레벨 조정 (개발 환경에서 너무 많은 로그 방지)
    if not app.config['DEBUG']:
        logging.getLogger('werkzeug').setLevel(logging.WARNING)
    
    app.logger.info('로깅 설정 완료')