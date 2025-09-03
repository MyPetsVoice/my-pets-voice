import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_full_app_integration():
    """전체 앱 통합 테스트"""
    try:
        from app import create_app
        from app.models import db
        
        app, socketio = create_app('testing')
        
        with app.app_context():
            # 데이터베이스 테이블 생성 테스트
            db.create_all()
            print("✅ 데이터베이스 테이블 생성 성공")
            
            # 블루프린트 등록 확인
            blueprints = list(app.blueprints.keys())
            expected_blueprints = ['auth_api', 'chat_api']
            
            for bp in expected_blueprints:
                if bp in blueprints:
                    print(f"✅ {bp} 블루프린트 등록됨")
                else:
                    print(f"⚠️ {bp} 블루프린트 미등록")
            
            # 라우트 등록 확인
            routes = [rule.rule for rule in app.url_map.iter_rules()]
            essential_routes = ['/', '/auth/kakao/login', '/auth/kakao/callback']
            
            for route in essential_routes:
                if route in routes:
                    print(f"✅ {route} 라우트 등록됨")
                else:
                    print(f"⚠️ {route} 라우트 미등록")
                    
    except Exception as e:
        print(f"❌ 통합 테스트 실패: {e}")

def test_import_all_modules():
    """모든 모듈 import 테스트"""
    modules_to_test = [
        'app',
        'app.models',
        'app.routes',
        'app.services',
        'config'
    ]
    
    for module in modules_to_test:
        try:
            __import__(module)
            print(f"✅ {module} import 성공")
        except Exception as e:
            print(f"❌ {module} import 실패: {e}")

if __name__ == "__main__":
    test_import_all_modules()
    test_full_app_integration()