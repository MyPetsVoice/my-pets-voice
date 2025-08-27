from flask import Blueprint, render_template, session, redirect, url_for

chat_views_bp = Blueprint('chat_views', __name__)

@chat_views_bp.route('/chat', methods=['GET'])
def chat():
    if 'pet_info' not in session: # user로 변경...?
        return redirect(url_for('index'))
    return render_template('chat/chat.html', pet_info=session['pet_info'])

# 필요에 따라 추가 라우트