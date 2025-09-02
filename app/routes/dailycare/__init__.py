from flask import Blueprint
from app.routes.dailycare.dailycare_api import dailycare_api_bp
from app.routes.dailycare.dailycare_views import dailycare_views_bp

dailycare_bp = Blueprint('dailycare', __name__)

dailycare_bp.register_blueprint(dailycare_views_bp, url_prefix='/dailycare')
dailycare_bp.register_blueprint(dailycare_api_bp, url_prefix='/api/dailycares')
