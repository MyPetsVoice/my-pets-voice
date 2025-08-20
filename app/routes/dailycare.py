from flask import Flask, Blueprint, jsonify

dailycare_bp = Blueprint('dailycare_bp', __name__)

@dailycare_bp.route('/dailycare', methods=['GET'])
def get_dailycare():
    return jsonify({"message": "Welcome to the Daily Care Blueprint!"}), 200

def create_app():
    app = Flask(__name__)
    app.register_blueprint(dailycare_bp)
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)