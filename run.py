from app import create_app

app, socketio = create_app()

if __name__=='__main__':
    import os
    debug_mode = os.getenv('FLASK_ENV') == 'development'
    socketio.run(app, debug=debug_mode, port=5000, host='0.0.0.0', allow_unsafe_werkzeug=True)