import requests
import os
from datetime import datetime
import xml.etree.ElementTree as ET

class WeatherService:
    def __init__(self):
        # 공공데이터포털에서 발급받은 API 키
        self.api_key = os.getenv('WEATHER_API_KEY')
        # 기상청 단기예보 API 기본 URL
        self.base_url = 'http://apis.data.go.kr/1360000/VilageFcstInfoService_2.0'
        
    def get_current_weather(self, location='서울'):
        # 지역명을 격자 좌표로 변환
        nx, ny = self.get_coordinates(location)
        
        # 현재 시간 기준으로 API 호출 시간 계산
        now = datetime.now()
        base_date = now.strftime('%Y%m%d')  # 오늘 날짜 (예: 20250902)
        
        # 기상청 초단기실황 API는 매시간 30분에 업데이트됨
        if now.minute >= 30:
            base_time = f"{now.hour:02d}30"
        else:
            hour = now.hour - 1 if now.hour > 0 else 23
            base_time = f"{hour:02d}30"
        
        # API 요청 파라미터 설정
        params = {
            'serviceKey': self.api_key,           # API 키
            'pageNo': 1,                          # 페이지 번호
            'numOfRows': 100,                     # 한 페이지에서 가져올 데이터 수
            'dataType': 'XML',                    # 응답 데이터 형식
            'base_date': base_date,               # 발표일자
            'base_time': base_time,               # 발표시각
            'nx': nx,                            # 예보지점 X 좌표
            'ny': ny                             # 예보지점 Y 좌표
        }
        
        # 현재 날씨 호출 (초단기)
        response = requests.get(f"{self.base_url}/getUltraSrtNcst", params=params)
        
        if response.status_code != 200:
            return None
            
        # XML 응답 파싱
        root = ET.fromstring(response.text)
        items = root.findall('.//item') 
        
        weather_data = {
            'temperature': None,  # 기온
            'sky_code': None,     # 날씨 상태 코드
            'location': location  # 지역명
        }
        
        # XML 데이터에서 필요한 정보만 추출
        for item in items:
            category = item.find('category').text    
            value = item.find('obsrValue').text        
            
            # T1H: 기온
            if category == 'T1H':
                weather_data['temperature'] = int(float(value))
            # PTY: 강수형태
            elif category == 'PTY':  
                weather_data['sky_code'] = int(value)
        
        # 날씨 코드 이용해서 이모지 변환
        weather_data['weather_text'] = self.get_weather_text(weather_data['sky_code'])
        weather_data['weather_emoji'] = self.get_weather_emoji(weather_data['sky_code'])
        
        return weather_data
    
    def get_coordinates(self, location):
        coordinates = {
            '서울': (60, 127),
            '부산': (98, 76),
            '대구': (89, 90),
            '인천': (55, 124),
            '광주': (58, 74),
            '대전': (67, 100),
            '울산': (102, 84),
            '경기': (60, 120),
            '강원': (73, 134),
            '충북': (69, 107),
            '충남': (68, 100),
            '전북': (63, 89),
            '전남': (51, 67),
            '경북': (87, 106),
            '경남': (91, 77),
            '제주': (52, 38)
        }
        # 기본 서울
        return coordinates.get(location, (60, 127))
    
    def get_weather_text(self, code):
        if code is None:
            return '맑음'
        
        weather_codes = {
            0: '맑음',
            1: '비',
            2: '비/눈',
            3: '눈',
            5: '빗방울',
            6: '진눈깨비',
            7: '눈날림'
        }
        return weather_codes.get(code, '맑음')
    
    def get_weather_emoji(self, code):
        if code is None:
            return '☀️'
            
        weather_emojis = {
            0: '☀️',   # 맑음
            1: '🌧️',   # 비
            2: '🌨️',   # 비/눈
            3: '❄️',   # 눈
            5: '🌦️',   # 빗방울
            6: '🌨️',   # 진눈깨비
            7: '❄️'    # 눈날림
        }
        return weather_emojis.get(code, '☀️')