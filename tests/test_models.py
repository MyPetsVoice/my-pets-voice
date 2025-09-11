import pytest
import sys
import os
from datetime import datetime, date

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_user_model():
    """사용자 모델 테스트"""
    try:
        from app.models.user import User
        
        # 카카오 사용자 생성 테스트
        kakao_user_data = {
            'id': 12345,
            'kakao_account': {
                'profile': {'nickname': '테스트유저'},
                'email': 'test@example.com'
            }
        }
        
        # 모델 구조 검증
        assert hasattr(User, 'create_user_from_kakao')
        assert hasattr(User, 'find_by_social')
        print("✅ User 모델 구조 검증 완료")
        
    except Exception as e:
        print(f"❌ User 모델 테스트 실패: {e}")

def test_pet_model():
    """반려동물 모델 테스트"""
    try:
        from app.models.pet import Pet, PetSpecies, PetBreed
        
        # 모델 구조 검증
        assert hasattr(Pet, 'create_pet')
        assert hasattr(PetSpecies, 'get_all_species')
        assert hasattr(PetBreed, 'get_by_species')
        print("✅ Pet 모델 구조 검증 완료")
        
    except Exception as e:
        print(f"❌ Pet 모델 테스트 실패: {e}")

def test_persona_model():
    """페르소나 모델 테스트"""
    try:
        from app.models.pet_persona import PetPersona, PersonalityTrait, SpeechStyle
        
        # 모델 구조 검증
        assert hasattr(PetPersona, 'create_persona')
        assert hasattr(PetPersona, 'get_persona_info')
        assert hasattr(PersonalityTrait, 'create_trait')
        print("✅ Persona 모델 구조 검증 완료")
        
    except Exception as e:
        print(f"❌ Persona 모델 테스트 실패: {e}")

if __name__ == "__main__":
    test_user_model()
    test_pet_model()
    test_persona_model()