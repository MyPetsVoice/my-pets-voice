from flask import Blueprint, render_template, redirect, url_for, session

diary_views_bp = Blueprint("diary_views", __name__)

@diary_views_bp.route("/")
def diary():
    user = session.get('user')
    if user:
        user_nickname = user['kakao_account']['profile']['nickname']
        return render_template('diary/diary.html', user=user_nickname)

    return redirect(url_for('index'))

@diary_views_bp.route("/write")
def write():
    user = session.get('user')
    if user:
        user_nickname = user['kakao_account']['profile']['nickname']
        return render_template("diary/write.html", user=user_nickname)

    return redirect(url_for('index'))

@diary_views_bp.route("/detail/<int:diary_id>")
def detail(diary_id):
    user = session.get('user')
    if user:
        user_nickname = user['kakao_account']['profile']['nickname']
        return render_template("diary/detail.html", diary_id=diary_id, user=user_nickname)
    
    return redirect(url_for('index'))
