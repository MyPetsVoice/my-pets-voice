from app.models import db
from app.models.base import BaseModel

class Pet(BaseModel):
    __tablename__ = 'pets'

    pet_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    pet_name = db.Column(db.String(50), nullable=False)
    pet_species = db.Column(db.String(30), nullable=False)
    pet_breed = db.Column(db.String(50))
    pet_age = db.Column(db.Integer)
    pet_gender = db.Column(db.String(10))
    is_neutered = db.Column(db.Boolean, default=False)
    profile_image_url = db.Column(db.String(500))

    user = db.relationship('User', backref='pets')
    
    def __repr__(self):
        return f'<Pet {self.pet_name}>'
    
    @classmethod
    def create_pet(cls, user_id, **kwargs):
        return cls.create(user_id=user_id, **kwargs)
    

class PetSpecies(BaseModel):
    __tablename__='pet_species'

    species_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    species_name = db.Column(db.String(50), unique=True, nullable=False)
    # species_name_en = db.Column(db.String(50), unique=True)
    # description = db.Column(db.Text)
    # is_active = db.Column(db.Boolean, default=True)
    # display_order = db.Column(db.Integer, default=0)

    breeds = db.relationship('PetBreed', backref='species', cascasde='all, delete-orphan')

    def __repr__(self):
        return f'<AnimalSpecies {self.species_name}>'
    
    @classmethod
    def get_all_species(cls):
        return cls.query.order_by(cls.species_name.asc()).all()
    
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
