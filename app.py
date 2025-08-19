from flask import Flask, render_template
from app.routes.converation_route import conversation_bp

app = Flask(__name__)

app.register_blueprint(conversation_bp)

@app.route('/')
def index():
    return render_template('base.html')


if __name__=='__main__':
    app.run(debug=True, port=5001)