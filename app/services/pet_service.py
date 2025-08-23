from app.models import db, Pet

class PetService:
    @staticmethod
    def get_all_pets():
        """모든 Pet 가져오기"""
        return Pet.query.all()

    @staticmethod
    def get_pet_by_id(pet_id: int):
        """pet_id로 Pet 하나 가져오기"""
        return Pet.query.get(pet_id)

    @staticmethod
    def get_pets_by_user(user_id: int):
        """특정 user가 등록한 Pet 가져오기"""
        return Pet.query.filter_by(user_id=user_id).all()
