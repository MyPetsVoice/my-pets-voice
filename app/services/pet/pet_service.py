from app.models import db, Pet, PetSpecies, PetBreed

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
    
    # PetService
    @staticmethod
    def get_pet(pet_id: int):
        pet = Pet.query.get(pet_id)
        return pet.to_dict() if pet else None




    @staticmethod
    def get_pets_by_user(user_id: int):
        """특정 user가 등록한 Pet 가져오기"""
        print('##### user_id : ',user_id)
        return Pet.query.filter_by(user_id=user_id).all()
    
    @staticmethod
    def get_all_species():
        """모든 펫 종 조회"""
        return PetSpecies.query.all()
    
    @staticmethod
    def get_breeds_by_species(species_id):
        """특정 종의 품종 목록 조회"""
        return PetBreed.query.filter_by(species_id=species_id).order_by(PetBreed.breed_name.asc()).all()
