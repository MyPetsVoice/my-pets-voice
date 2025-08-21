from flask import Flask, render_template
from app.routes.diary import diary_bp

def create_app():
    app = Flask(__name__)

    @app.route('/')
    def index():
        return render_template('base.html')

    # 블루프린트 등록 위치
    # app.register_blueprint(some_blueprint)
    app.register_blueprint(diary_bp, url_prefix="/diary")

    return app
