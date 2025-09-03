import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_app_routes():
    """라우트 등록 테스트"""
    try:
        from app import create_app
        
        app, socketio = create_app('testing')
        
        with app.test_client() as client:
            # 메인 페이지 테스트
            response = client.get('/')
            assert response.status_code == 200
            print("✅ 메인 페이지 접근 성공")
            
            # 존재하지 않는 페이지 테스트
            response = client.get('/nonexistent')
            assert response.status_code == 404
            print("✅ 404 에러 처리 정상")
            
    except Exception as e:
        print(f"❌ 라우트 테스트 실패: {e}")

def test_auth_routes():
    """인증 라우트 테스트"""
    try:
        from app import create_app
        
        app, socketio = create_app('testing')
        
        with app.test_client() as client:
            # 카카오 로그인 페이지 리다이렉트 테스트
            response = client.get('/auth/kakao/login')
            assert response.status_code == 302  # 리다이렉트
            print("✅ 카카오 로그인 리다이렉트 정상")
            
    except Exception as e:
        print(f"❌ 인증 라우트 테스트 실패: {e}")

if __name__ == "__main__":
    test_app_routes()
    test_auth_routes()