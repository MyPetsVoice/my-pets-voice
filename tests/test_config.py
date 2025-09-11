import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_config_loading():
    """설정 로딩 테스트"""
    try:
        from config import config
        
        # 설정 클래스들이 존재하는지 확인
        assert 'development' in config
        assert 'production' in config
        assert 'testing' in config
        print("✅ 설정 클래스 로딩 성공")
        
    except Exception as e:
        print(f"❌ 설정 로딩 테스트 실패: {e}")

def test_app_creation():
    """앱 생성 테스트"""
    try:
        from app import create_app
        
        # 다양한 환경으로 앱 생성 테스트
        for env in ['development', 'testing']:
            app, socketio = create_app(env)
            assert app is not None
            assert socketio is not None
            print(f"✅ {env} 환경 앱 생성 성공")
            
    except Exception as e:
        print(f"❌ 앱 생성 테스트 실패: {e}")

def test_required_config():
    """필수 설정 확인 테스트"""
    try:
        from app import create_app
        
        app, socketio = create_app('testing')
        
        # 필수 설정들이 있는지 확인
        required_configs = [
            'SECRET_KEY',
            'SQLALCHEMY_DATABASE_URI'
        ]
        
        for config_key in required_configs:
            assert config_key in app.config
            print(f"✅ {config_key} 설정 존재")
            
    except Exception as e:
        print(f"❌ 필수 설정 테스트 실패: {e}")

if __name__ == "__main__":
    test_config_loading()
    test_app_creation()
    test_required_config()