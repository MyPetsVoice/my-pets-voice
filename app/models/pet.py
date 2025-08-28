from app.models import db
from app.models.base import BaseModel
from sqlalchemy.orm import joinedload
import logging

logger = logging.getLogger(__name__)

class Pet(BaseModel):
    __tablename__ = 'pets'

    pet_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    pet_name = db.Column(db.String(50), nullable=False)
    species_id = db.Column(db.Integer, db.ForeignKey('pet_species.species_id'), nullable=False)
    breed_id = db.Column(db.Integer, db.ForeignKey('pet_breeds.breed_id'))
    pet_age = db.Column(db.Integer)
    birthdate = db.Column(db.Date)
    adoption_date = db.Column(db.Date)
    pet_gender = db.Column(db.String(10))
    is_neutered = db.Column(db.Boolean, default=False)
    profile_image_url = db.Column(db.String(500))

    user = db.relationship('User', backref='pets')
    species = db.relationship('PetSpecies', backref='pets', lazy='joined')
    breeds = db.relationship('PetBreed', backref='pets', lazy='joined')
    
    # PetPersona와의 관계 - Pet 삭제시 PetPersona도 함께 삭제
    persona = db.relationship('PetPersona', backref='pet', cascade='all, delete-orphan', uselist=False)
    
    def __repr__(self):
        return f'<Pet {self.pet_name}>'
    
    @classmethod
    def create_pet(cls, user_id, **kwargs):
        return cls.create(user_id=user_id, **kwargs)
    
    @classmethod
    def find_pets_by_user_id(cls, user_id):
        # N+1 쿼리 문제 해결: 관련 데이터를 한 번에 조회
        return cls.query.filter_by(user_id=user_id).options(
            joinedload(cls.species),
            joinedload(cls.breeds)
        ).all()
    
    @classmethod
    def find_pet_by_pet_id(cls, pet_id):
        pet = cls.query.filter_by(pet_id=pet_id).first()
        return pet.to_dict()

    def to_dict(self):
        return {
            'pet_id': self.pet_id,
            'user_id': self.user_id,
            'pet_name': self.pet_name,
            'species_id': self.species_id,
            'species_name': self.species.species_name if self.species else None,
            'breed_id': self.breed_id,
            'breed_name': self.breeds.breed_name if self.breeds else None,
            'pet_age': self.pet_age,
            'birthdate': self.birthdate.isoformat() if self.birthdate else None,
            'adoption_date': self.adoption_date.isoformat() if self.adoption_date else None,
            'pet_gender': self.pet_gender,
            'is_neutered': self.is_neutered,
        }

class PetSpecies(BaseModel):
    __tablename__='pet_species'

    species_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    species_name = db.Column(db.String(50), unique=True, nullable=False)
    # species_name_en = db.Column(db.String(50), unique=True)
    # description = db.Column(db.Text)
    # is_active = db.Column(db.Boolean, default=True)
    # display_order = db.Column(db.Integer, default=0)

    breeds = db.relationship('PetBreed', backref='species', cascade='all, delete-orphan')

    def __repr__(self):
        return f'<AnimalSpecies {self.species_name}>'
    
    @classmethod
    def get_all_species(cls):
        return cls.query.all()
    
    @classmethod
    def create_species(cls, species_name):
        return cls.create(species_name=species_name)

    def to_dict(self):
        return {'species_id': self.species_id, 'species_name': self.species_name}


class PetBreed(BaseModel):
    __tablename__ = 'pet_breeds'

    breed_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    species_id = db.Column(db.Integer, db.ForeignKey('pet_species.species_id'), nullable=False)
    breed_name = db.Column(db.String(50))

    def __repr__(self):
        return f'<PetBreed {self.breed_name}'
    
    @classmethod
    def get_by_species(cls, species_id):
        return cls.query.filter_by(species_id=species_id).order_by(cls.breed_name.asc()).all()
    
    @classmethod
    def create_breed(cls, species_id, breed_name):
        return cls.create(species_id=species_id, breed_name=breed_name)

    def to_dict(self):
        return {
            'breed_id': self.breed_id,
            'species_id': self.species_id,
            'breed_name': self.breed_name
        }




if __name__=='__main__':
    print(PetSpecies.get_all_species())