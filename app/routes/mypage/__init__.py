from flask import Blueprint
from app.routes.mypage.mypage_api import mypage_api_bp
from app.routes.mypage.mypage_views import mypage_views_bp

mypage_bp = Blueprint('mypage', __name__)

mypage_bp.register_blueprint(mypage_views_bp)
mypage_bp.register_blueprint(mypage_api_bp, url_prefix='/api')