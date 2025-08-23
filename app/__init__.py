from flask import Flask, render_template
from app.routes.diary import diary_bp
from app.routes.diary.diary_api import diary_api_bp
from app.routes.chat.chat import chat_bp
from app.routes.chat.chat_api import chat_api_bp
from app.models import init_db

import os

def create_app():
    app = Flask(__name__)
    
    # 데이터베이스 설정
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///mypetsvoice.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = 'your-secret-key-here'
    
    # 파일 업로드 (일기..)
    app.config['UPLOAD_FOLDER'] = 'app/static/uploads'
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
    
    upload_dir = os.path.join(app.root_path, 'static', 'uploads', 'diary')
    os.makedirs(upload_dir, exist_ok=True)
    
    # 데이터베이스 초기화
    init_db(app)

    @app.route('/')
    def index():
        return render_template('base.html')

    # 블루프린트 등록 위치
    # app.register_blueprint(some_blueprint)
    app.register_blueprint(diary_bp, url_prefix="/diary")
    app.register_blueprint(diary_api_bp, url_prefix="/api/diary")
    app.register_blueprint(chat_bp)
    app.register_blueprint(chat_api_bp)

    return app
