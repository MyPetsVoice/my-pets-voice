from flask import Blueprint, request, jsonify

chat_bp = Blueprint('chat', __name__)

@chat_bp.route('/chat', methods=['GET'])
def get_conversation():
    return jsonify({"message": "Hello from conversation blueprint!"})

# 필요에 따라 추가 라우트