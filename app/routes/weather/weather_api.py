from flask import Blueprint, jsonify, request
from app.services.weather.weather_service import WeatherService

# 날씨 API 블루프린트 생성
weather_api_bp = Blueprint('weather_api', __name__)

@weather_api_bp.route('/current')
def get_current_weather():
    # URL 파라미터에서 지역명 가져오기 (기본값: 서울)
    location = request.args.get('location', '서울')
    
    # 인스턴스 생성
    weather_service = WeatherService()
    
    # 날씨 정보 조회
    weather_data = weather_service.get_current_weather(location)
    
    if weather_data and weather_data['temperature'] is not None:
        return jsonify({
            'success': True,
            'location': location,
            'temperature': weather_data['temperature'],      # 온도
            'weather_text': weather_data['weather_text'],    # 날씨 상태
            'weather_emoji': weather_data['weather_emoji']   # 이모지
        })
    
    # 데이터를 가져오지 못한 경우
    return jsonify({
        'success': False,
        'message': '날씨 정보를 가져올 수 없습니다.'
    }), 500

@weather_api_bp.route('/locations')
def get_locations():
    
    # 지원 지역 리스트
    locations = [
        '서울', '부산', '대구', '인천', '광주', '대전', '울산', 
        '경기', '강원', '충북', '충남', '전북', '전남', '경북', '경남', '제주'
    ]
    
    return jsonify({
        'success': True,
        'locations': locations
    })

@weather_api_bp.route('/widget')
def get_weather_widget():

    location = request.args.get('location', '서울')
    
    weather_service = WeatherService()
    weather_data = weather_service.get_current_weather(location)
    
    # 위젯용 데이터 반환
    if weather_data and weather_data['temperature'] is not None:
        return jsonify({
            'success': True,
            'location': location,
            'temperature': weather_data['temperature'],
            'weather_emoji': weather_data['weather_emoji'],
            'weather_text': weather_data['weather_text']
        })
    
    return jsonify({
        'success': False,
        'message': '날씨 정보를 가져올 수 없습니다.'
    }), 500