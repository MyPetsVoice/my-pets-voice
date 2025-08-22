from flask import Blueprint, render_template

mypage_views_bp = Blueprint('mypage_views', __name__)

@mypage_views_bp.route('/mypage')
def mypage():

    return render_template('mypage/mypage.html')