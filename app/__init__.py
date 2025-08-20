from flask import Flask, render_template

def create_app():
    app = Flask(__name__)

    @app.route('/')
    def index():
        return render_template('base.html')

    # 블루프린트 등록 위치
    # app.register_blueprint(some_blueprint)

    return app
