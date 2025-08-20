from flask import Flask, render_template
from app.routes.chat.chat import chat_bp
from app.routes.chat.chat_api import api_chat_bp

app = Flask(__name__)

app.register_blueprint(chat_bp)
app.register_blueprint(api_chat_bp)


@app.route('/')
def index():
    return render_template('base.html')



if __name__=='__main__':
    app.run(debug=True, port=5001)