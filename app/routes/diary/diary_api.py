from flask import Blueprint, jsonify

diary_api_bp = Blueprint("diary_api", __name__, url_prefix="/api")

@diary_api_bp.route("/list")
def list_diaries():
    
    return jsonify({"message": "일기"})