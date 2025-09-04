from flask import Blueprint
from .weather_api import weather_api_bp

weather_bp = Blueprint('weather', __name__)

weather_bp.register_blueprint(weather_api_bp, url_prefix='/api/weather/')