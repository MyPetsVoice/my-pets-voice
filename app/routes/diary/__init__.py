from flask import Blueprint
from .diary_views import diary_views_bp
from .diary_api import diary_api_bp

diary_bp = Blueprint('diary', __name__)

diary_bp.register_blueprint(diary_views_bp, url_prefix='/diary/')
diary_bp.register_blueprint(diary_api_bp, url_prefix='/api/diary/')

