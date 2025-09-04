from flask import Flask, render_template
from flask_socketio import SocketIO
from app.routes import register_blueprints
from app.models import init_db
from config import config, setup_logging
from dotenv import load_dotenv
import os

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
    
    # 정적 파일 캐시 버스팅
    import time
    app.config['STATIC_VERSION'] = str(int(time.time()))
    
    @app.context_processor
    def inject_static_version():
        return {'static_version': app.config['STATIC_VERSION']}
    
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
    
    # 블루프린트 등록
    app.logger.info('블루프린트를 등록합니다.')
    register_blueprints(app)
    app.logger.info('모든 블루프린트가 등록되었습니다.')
    
    # chat_api_bp의 socketio 초기화 (블루프린트 등록 후)
    from app.routes.chat.chat_api import init_socketio
    init_socketio(socketio, app)
    app.logger.info('채팅 API SocketIO가 초기화되었습니다.')

    @app.route('/')
    def index():
        app.logger.debug('루트 경로 접근 - 랜딩페이지')
        return render_template('landing.html')
    
    # HTML 응답의 캐시 방지
    @app.after_request
    def after_request(response):
        if response.content_type.startswith('text/html'):
            response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
            response.headers['Pragma'] = 'no-cache'
            response.headers['Expires'] = '0'
        return response

    app.logger.info('애플리케이션 초기화가 완료되었습니다.')
    return app, socketio
