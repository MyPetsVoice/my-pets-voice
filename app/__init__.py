from flask import Flask, render_template, redirect, url_for
from app.routes.diary import diary_bp
from app.routes.diary.diary_api import diary_api_bp
from app.routes.chat.chat_api import chat_api_bp
from app.routes.dailycare.dailycare_api import dailycare_api_bp
from app.routes.dailycare.dailycare_view import dailycare_bp 
from flask_socketio import SocketIO
from app.routes.chat import chat_bp
from app.routes.auth import auth_bp
from app.routes.mypage import mypage_bp
from app.models import init_db
from config import config, setup_logging
import os


from dotenv import load_dotenv
load_dotenv()
def create_app(config_name=None):
    app = Flask(__name__)
    
    # 설정 로드
    if config_name is None:
        config_name = os.getenv('FLASK_ENV', 'default')
    
    app.config.from_object(config[config_name])
    
    # 로깅 설정
    setup_logging(app)
    app.logger.info(f'{config_name} 환경으로 애플리케이션이 시작되었습니다.')
    
    # 파일 업로드 (일기..)
    app.config['UPLOAD_FOLDER'] = 'app/static/uploads'
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
    
    upload_dir = os.path.join(app.root_path, 'static', 'uploads', 'diary')
    os.makedirs(upload_dir, exist_ok=True)
    
    # 데이터베이스 초기화
    app.logger.info('데이터베이스를 초기화합니다.')
    init_db(app)

    # SocketIO 초기화
    app.logger.info('SocketIO를 초기화합니다.')
    socketio = SocketIO(
        app, 
        cors_allowed_origins="*", 
        async_mode='threading',
        engineio_logger=False,
        socketio_logger=False,
        ping_timeout=60,
        ping_interval=25
    )
    
    # chat_api_bp의 socketio 초기화
    from app.routes.chat.chat_api import init_socketio
    init_socketio(socketio, app)
    app.logger.info('채팅 API SocketIO가 초기화되었습니다.')

    @app.route('/')
    def index():
        app.logger.debug('루트 경로 접근 - 랜딩페이지')
        return render_template('landing.html')

    # 블루프린트 등록 위치
    # app.register_blueprint(some_blueprint)
    app.logger.info('블루프린트를 등록합니다.')
    app.register_blueprint(diary_bp, url_prefix="/diary")
    app.register_blueprint(diary_api_bp, url_prefix="/api/diary")
    # 블루프린트 등록
    app.register_blueprint(dailycare_bp , url_prefix='/dailycare') 
    app.register_blueprint(dailycare_api_bp)
    app.register_blueprint(chat_bp)
    app.register_blueprint(chat_api_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(mypage_bp)
    app.logger.info('모든 블루프린트가 등록되었습니다.')
    app.logger.info('애플리케이션 초기화가 완료되었습니다.')
    return app, socketio
