from app import create_app
from app.models.pet_persona import PetPersona

if __name__=='__main__':
    # Flask 애플리케이션 생성 및 컨텍스트 설정
    app, socketio = create_app()
    
    with app.app_context():
        # get_persona_info 메서드 테스트
        try:
            # 테스트할 pet_id (실제 존재하는 ID로 변경 필요)
            test_pet_id = 1
            
            # PetPersona 인스턴스 생성
            pet_persona = PetPersona()
            
            print(f"Testing get_persona_info with pet_id: {test_pet_id}")
            
            # get_persona_info 메서드 테스트
            result = pet_persona.get_persona_info(test_pet_id)
            
            print("테스트 결과:")
            print(f"Persona ID: {result.get('pet_persona_id')}")
            print(f"User ID: {result.get('user_id')}")
            print(f"Pet ID: {result.get('pet_id')}")
            print(f"User Call: {result.get('user_call')}")
            print(f"Politeness: {result.get('politeness')}")
            print(f"Speech Habit: {result.get('speech_habit')}")
            print(f"Likes: {result.get('likes')}")
            print(f"Dislikes: {result.get('dislikes')}")
            print(f"Habits: {result.get('habits')}")
            print(f"Family Info: {result.get('family_info')}")
            print(f"Special Note: {result.get('special_note')}")
            print(f"Traits: {result.get('traits')}")
            print(f"Style Name: {result.get('style_name')}")
            
        except Exception as e:
            print(f"테스트 중 오류 발생: {e}")
            print(f"오류 타입: {type(e).__name__}")
    