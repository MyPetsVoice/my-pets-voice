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
    
    # 벡터 DB 초기화 (환경 변수로 제어)
    skip_vector_init = os.getenv('SKIP_VECTOR_INIT', 'false').lower() == 'true'
    if not skip_vector_init:
        app.logger.info('벡터 DB를 초기화합니다.')
        try:
            from app.services.dailycare.vectorstore_service import VectorStoreService
            vector_service = VectorStoreService()
            vector_service.initialize_vector_db()
            app.logger.info('벡터 DB 초기화가 완료되었습니다.')
        except Exception as e:
            app.logger.error(f'벡터 DB 초기화 중 오류 발생: {e}')
            app.logger.warning('벡터 DB 없이 애플리케이션을 계속 실행합니다.')
    else:
        app.logger.info('SKIP_VECTOR_INIT=true 설정으로 벡터 DB 초기화를 건너뜁니다.')

    @app.route('/')
    def index():
        app.logger.debug('루트 경로 접근 - 랜딩페이지')
        return render_template('landing.html')


    @app.route('/health')
    def health_check():
        """헬스체크 엔드포인트"""
        try:
            # 데이터베이스 연결 확인
            from app.models import db
            from sqlalchemy import text
            db.session.execute(text('SELECT 1'))
            return {'status': 'healthy', 'database': 'connected'}, 200
        except Exception as e:
            app.logger.error(f'헬스체크 실패: {e}')
            return {'status': 'unhealthy', 'error': str(e)}, 503

    app.logger.info('애플리케이션 초기화가 완료되었습니다.')
    return app, socketio
