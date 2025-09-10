from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for
from app.models.pet import Pet
from app.models.pet_persona import PetPersona
from app.models import db
import json
import logging

logger = logging.getLogger(__name__)

mypage_views_bp = Blueprint('mypage_views', __name__)


@mypage_views_bp.route('/mypage')
def mypage():
    user = session.get('user')
    logger.info(f'로그인 한 사용자 정보 조회 : {user}')
    if user:
        user_nickname = user['kakao_account']['profile']['nickname']
        user_profile_img = user['kakao_account']['profile']['profile_image_url']

        return render_template('mypage/mypage.html', user=user_nickname, profile_img_url = user_profile_img)

    return redirect(url_for('index')) 
