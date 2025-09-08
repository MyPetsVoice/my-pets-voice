import os
from app import create_app

app, socketio = create_app()

if __name__=='__main__':
    # 환경에 따라 debug 모드 결정
    debug_mode = os.getenv('FLASK_ENV', 'production') != 'production'
    socketio.run(app, debug=debug_mode, port=5000, host='0.0.0.0', allow_unsafe_werkzeug=True)