from flask import Blueprint
from app.routes.chat.chat_views import chat_views_bp
from app.routes.chat.chat_api import chat_api_bp

chat_bp = Blueprint('chat', __name__)

chat_bp.register_blueprint(chat_views_bp)
chat_bp.register_blueprint(chat_api_bp, url_prefix='/api')