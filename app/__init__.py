from flask import Flask, render_template
from flask import Blueprint
from app.routes.dailycare import dailycare_bp #dailycare 
def create_app():
    app = Flask(__name__)

    @app.route('/')
    def index():
        return render_template('base.html')

    # 블루프린트 등록 위치
    app.register_blueprint(dailycare_bp, url_prefix='/dailycare') #dailycare

    return app
