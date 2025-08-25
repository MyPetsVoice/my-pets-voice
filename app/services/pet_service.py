from app.models import db, Pet

class PetService:
    @staticmethod
    def get_all_pets():
        """모든 Pet 가져오기"""
        return Pet.query.all()

    @staticmethod
    def get_pet_by_id(pet_id: int, user_id: int = None):
        """pet_id로 Pet 하나 가져오기, 필요 시 user_id 확인"""
        query = Pet.query.filter_by(pet_id=pet_id)
        
        if user_id is not None:
            query = query.filter_by(user_id=user_id)
        
        pet = query.first()  
        return pet
    
    @staticmethod
    def get_pet(pet_id: int,):
        """pet_id로 Pet 하나 가져오기"""
        query = Pet.query.filter_by(pet_id=pet_id)
        
        pet = query.first()  
        return pet



    @staticmethod
    def get_pets_by_user(user_id: int):
        """특정 user가 등록한 Pet 가져오기"""
        print('##### user_id : ',user_id)
        return Pet.query.filter_by(user_id=user_id).all()
