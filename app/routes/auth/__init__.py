from flask import Blueprint
from app.routes.auth.auth_api import auth_api_bp

auth_bp = Blueprint('auth', __name__)

auth_bp.register_blueprint(auth_api_bp)