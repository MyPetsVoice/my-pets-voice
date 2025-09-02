from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for
from app.models.pet import Pet
from app.models.pet_persona import PetPersona
from app.models import db
import json

mypage_views_bp = Blueprint('mypage_views', __name__)


@mypage_views_bp.route('/mypage')
def mypage():
    user = session.get('user')
    if user:
        user_nickname = user['kakao_account']['profile']['nickname']
        return render_template('mypage/mypage.html', user=user_nickname)

    return redirect(url_for('index')) 
