from flask import Blueprint, request, jsonify, redirect, session, url_for, render_template
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
    # 2. 인가 코드 받아서 액세스 토큰 요청
    code = request.args.get('code')

    if not code:
        return '인증코드가 없습니다.', 400
    print('발급된 code : ', code)

    # 액세스 토큰 요청에 필요한 파라미터 구성
    data = {
        'grant_type': 'authorization_code',  # 인증 방식 고정값
        'client_id': KAKAO_CLIENT_ID,              # 내 앱의 REST API 키
        'redirect_uri': KAKAO_REDIRECT_URI,        # 등록된 리다이렉트 URI
        'client_secret': KAKAO_CLIENT_SECRET,      # 선택: 클라이언트 시크릿(Client Secret) 사용 시 추가
        'code': code    # 전달받은 인가 코드
    }

    # 개발자 문서에는 헤더를 포함해야한다고 되어있음.
    # header = {"Content-Type: application/x-www-form-urlencoded;charset=utf-8"} 

    # 카카오 인증 서버에 액세스 토큰 post 요청
    resp = requests.post(KAUTH_HOST + "/oauth/token", data=data) # 자동으로 헤더 추가해줌.
    print('액세스 토큰 요청 응답 : ', resp)


    # 발급받은 액세스 토큰을 세션에 저장 (로그인 상태 유지 목적)
    session['access_token'] = resp.json()['access_token']
    print('액세스 토큰 : ', resp.json()['access_token'])

    # 사용자 정보 요청위한 헤더
    headers = {
        'Authorization': 'Bearer ' + session.get('access_token', '')  # 세션에 저장된 액세스 토큰 전달
    }

    # 사용자 정보 조회 API GET 요청 전송
    user_info = requests.get(KAPI_HOST + "/v2/user/me", headers=headers)  
    user = user_info.json()['kakao_account']
    print('사용자 정보 : ', user)
    session['user'] = user
    '''
    {'id': 4408942414, 
    'connected_at': '2025-08-22T09:12:57Z', 
    'properties': {'nickname': '김태민', 
        'profile_image': 'http://img1.kakaocdn.net/thumb/R640x640.q70/?fname=http://t1.kakaocdn.net/account_images/default_profile.jpeg', 'thumbnail_image': 'http://img1.kakaocdn.net/thumb/R110x110.q70/?fname=http://t1.kakaocdn.net/account_images/default_profile.jpeg'
        },      
    'kakao_account': {'profile_nickname_needs_agreement': False, 
        'profile_image_needs_agreement': False, 
        'profile': 
            {'nickname': '김태민', 
            'thumbnail_image_url': 'http://img1.kakaocdn.net/thumb/R110x110.q70/?fname=http://t1.kakaocdn.net/account_images/default_profile.jpeg',
            'profile_image_url': 'http://img1.kakaocdn.net/thumb/R640x640.q70/?fname=http://t1.kakaocdn.net/account_images/default_profile.jpeg', 'is_default_image': True, 
            'is_default_nickname': False}, 
            'has_email': True, 
            'email_needs_agreement': False, 
            'is_email_valid': True, 
            'is_email_verified': True, 
            'email': 'lorraine10@daum.net'}
            }
    '''

    # 사용자 정보 저장 로직

    return redirect(url_for('mypage.mypage_views.mypage', user=user))


# 현재는 로그인/로그아웃 상태에 따른 차이가 없는 상황. 추후 수정
@auth_api_bp.route('/logout')
def logout():
    url = (f'https://kauth.kakao.com/oauth/logout?'
           f'client_id={KAKAO_CLIENT_ID}&logout_redirect_uri=http://127.0.0.1:5000&state=logout')
    print('로그아웃')
    # 세션 삭제는 안 해도 되는거임?

    return redirect(url) # 나중에 로그인 안 한 사용자들한테 보이는 페이지로 이동하도록 변경