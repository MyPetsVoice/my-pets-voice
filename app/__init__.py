from flask import Flask, render_template
from app.routes.chat.chat import chat_bp
from app.routes.chat.chat_api import chat_api_bp
from app.routes.auth.auth_api import auth_api_bp
from app.models import init_db
import os

def create_app():
    app = Flask(__name__)
    
    # 데이터베이스 설정
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///mypetsvoice.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


    # 로그인 세션
    app.config['SECRET_KEY'] = os.getenv('SESSION_SECRET_KEY')
    
    
    # 데이터베이스 초기화
    init_db(app)

    @app.route('/')
    def index():
        return render_template('base.html')

    # 블루프린트 등록 위치
    app.register_blueprint(chat_bp)
    app.register_blueprint(chat_api_bp)
    app.register_blueprint(auth_api_bp)

    return app
