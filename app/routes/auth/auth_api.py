from flask import Blueprint, request, jsonify, redirect, session, url_for
import requests
from dotenv import load_dotenv
import os

load_dotenv()

auth_api_bp = Blueprint('auth_api', __name__)

KAKAO_CLIENT_ID = os.getenv('KAKAO_REST_API_KEY')
KAKAO_CLIENT_SECRET = os.getenv('KAKAO_CLIENT_SECRET')
KAKAO_REDIRECT_URI = os.getenv('KAKAO_REDIRECT_URI')

KAPI_HOST="https://kapi.kakao.com"
KAUTH_HOST="https://kauth.kakao.com"


@auth_api_bp.route('/auth')
def kakao_login():
    # 1.인가 요청
    kakao_auth_url = (
        # 카카오 로그인 주소 엔드포이트 찾아오기, 또한 필요한 입력값들 확인하기
        f'{KAUTH_HOST}/oauth/authorize?'
        f'client_id={KAKAO_CLIENT_ID}&'
        f'redirect_uri={KAKAO_REDIRECT_URI}&'
        f'response_type=code&'
        f'scope=profile_nickname,profile_image,account_email'
    )
    return redirect(kakao_auth_url)


@auth_api_bp.route('/auth/kakao/callback')
def kakao_callback():
    # 2. 인가 코드 받아서 토큰 요청
    print('request : ', request)
    code = request.args.get('code')

    if not code:
        return '인증코드가 없습니다.', 400
    print('발급된 code : ', code)

    # 인가 코드 발급 요청에 필요한 파라미터 구성
    data = {
        'grant_type': 'authorization_code',  # 인증 방식 고정값
        'client_id': KAKAO_CLIENT_ID,              # 내 앱의 REST API 키
        'redirect_uri': KAKAO_REDIRECT_URI,        # 등록된 리다이렉트 URI
        'client_secret': KAKAO_CLIENT_SECRET,      # 선택: 클라이언트 시크릿(Client Secret) 사용 시 추가
        'code': code    # 전달받은 인가 코드
    }

    # header = {"Content-Type: application/x-www-form-urlencoded;charset=utf-8"}

    # 카카오 인증 서버에 액세스 토큰 요청
    resp = requests.post(KAUTH_HOST + "/oauth/token", data=data)
    print('액세스 토큰 요청 응답 : ', resp)


    # 발급받은 액세스 토큰을 세션에 저장 (로그인 상태 유지 목적)
    session['access_token'] = resp.json()['access_token']
    print('액세스 토큰 : ', resp.json()['access_token'])

    # 사용자 정보 요청
    headers = {
        'Authorization': 'Bearer ' + session.get('access_token', '')  # 세션에 저장된 액세스 토큰 전달
    }

    user_info = requests.get(KAPI_HOST + "/v2/user/me", headers=headers)  # 사용자 정보 조회 API 요청 전송
    print('사용자 정보 : ', user_info.json())
    user = user_info.json()['kakao_account']
    session['user'] = user
    return redirect(url_for('profile', user=user))