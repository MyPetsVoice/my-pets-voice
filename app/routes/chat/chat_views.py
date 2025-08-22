from flask import Blueprint, render_template

chat_views_bp = Blueprint('chat_views', __name__)

@chat_views_bp.route('/chat', methods=['GET'])
def chat():

    return render_template('chat/chat.html')

# 필요에 따라 추가 라우트