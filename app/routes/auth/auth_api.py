from flask import Blueprint, request, redirect, session, url_for, current_app
from app.models.user import User
import requests
import logging

logger = logging.getLogger(__name__)

auth_api_bp = Blueprint('auth_api', __name__)

@auth_api_bp.route('/auth')
def kakao_login():
    """카카오 로그인 인증 요청"""
    # config에서 설정값 가져오기
    client_id = current_app.config['KAKAO_REST_API_KEY']
    redirect_uri = current_app.config['KAKAO_REDIRECT_URI']
    kauth_host = current_app.config['KAUTH_HOST']
    
    # 카카오 로그인 주소 구성
    kakao_auth_url = (
        f'{kauth_host}/oauth/authorize?'
        f'client_id={client_id}&'
        f'redirect_uri={redirect_uri}&'
        f'response_type=code&'
        f'scope=profile_nickname,profile_image,account_email'
    )
    
    logger.info('카카오 로그인 인증 요청 시작')
    return redirect(kakao_auth_url)


@auth_api_bp.route('/auth/kakao/callback')
def kakao_callback():
    """카카오 로그인 콜백 처리"""
    code = request.args.get('code')
    
    if not code:
        logger.error('인증코드가 없습니다.')
        return '인증코드가 없습니다.', 400
    
    logger.debug(f'발급된 code: {code}')
    
    # config에서 설정값 가져오기
    client_id = current_app.config['KAKAO_REST_API_KEY']
    client_secret = current_app.config['KAKAO_CLIENT_SECRET']
    redirect_uri = current_app.config['KAKAO_REDIRECT_URI']
    kauth_host = current_app.config['KAUTH_HOST']
    kapi_host = current_app.config['KAPI_HOST']
    
    try:
        # 액세스 토큰 요청
        token_data = {
            'grant_type': 'authorization_code',
            'client_id': client_id,
            'redirect_uri': redirect_uri,
            'client_secret': client_secret,
            'code': code
        }
        
        token_response = requests.post(f'{kauth_host}/oauth/token', data=token_data)
        token_response.raise_for_status()  # HTTP 에러 체크
        
        token_info = token_response.json()
        access_token = token_info['access_token']
        
        # 세션에 액세스 토큰 저장
        session['access_token'] = access_token
        logger.debug(f'액세스 토큰 발급 성공: {access_token[:10]}...')
        
        # 사용자 정보 요청
        headers = {'Authorization': f'Bearer {access_token}'}
        user_response = requests.get(f'{kapi_host}/v2/user/me', headers=headers)
        user_response.raise_for_status()
        
        kakao_user_info = user_response.json()
        logger.debug(f'사용자 정보 조회 성공: {kakao_user_info.get("id")}')
        
        # 사용자 정보를 세션에 저장
        session['user'] = kakao_user_info
        
        # 기존 사용자 확인 및 처리
        existing_user = User.find_by_social('kakao', str(kakao_user_info['id']))
        if existing_user:
            existing_user.update_last_login()
            user = existing_user
            logger.info(f'기존 사용자 로그인: {user.user_id}')
        else:
            user = User.create_user_from_kakao(kakao_user_info)
            logger.info(f'신규 사용자 가입: {user.user_id}')
        
        session['user_id'] = user.user_id
        
        return redirect(url_for('mypage.mypage_views.mypage'))
        
    except requests.RequestException as e:
        logger.error(f'카카오 API 요청 실패: {str(e)}')
        return '로그인 처리 중 오류가 발생했습니다.', 500
    except Exception as e:
        logger.error(f'로그인 처리 중 예상치 못한 오류: {str(e)}')
        return '로그인 처리 중 오류가 발생했습니다.', 500


@auth_api_bp.route('/logout')
def logout():
    """로그아웃 처리"""
    try:
        client_id = current_app.config['KAKAO_REST_API_KEY']
        logout_redirect_uri = current_app.config.get('KAKAO_LOGOUT_REDIRECT_URI')

        # 세션 정보 삭제
        user_id = session.get('user_id')
        session.clear()
        
        logger.info(f'사용자 로그아웃: {user_id}')
        
        # 카카오 로그아웃 URL 구성
        kakao_logout_url = (
            f'https://kauth.kakao.com/oauth/logout?'
            f'client_id={client_id}&'
            f'logout_redirect_uri={logout_redirect_uri}&'
            f'state=logout'
        )
        
        return redirect(kakao_logout_url)
        
    except Exception as e:
        logger.error(f'로그아웃 처리 중 오류: {str(e)}')
        session.clear()  # 세션은 삭제
        return redirect(url_for('mypage.mypage_views.mypage'))