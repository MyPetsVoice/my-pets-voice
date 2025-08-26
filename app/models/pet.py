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
    medications = db.relationship('Medication', back_populates='pet', cascade='all, delete-orphan')
    allergies = db.relationship('Allergy', back_populates='pet', cascade='all, delete-orphan')
    diseases = db.relationship('Disease', back_populates='pet', cascade='all, delete-orphan')
    surgeries = db.relationship('Surgery', back_populates='pet', cascade = 'all, delete-orphan')
    vaccinations = db.relationship('Vaccination', back_populates='pet', cascade = 'all, delete-orphan')
    health_care = db.relationship('HealthCare', back_populates='pet', cascade = 'all, delete-orphan')
    
    
    
    
    def __repr__(self):
        return f'<Pet {self.pet_name}>'
    
    @classmethod
    def create_pet(cls, user_id, **kwargs):
        return cls.create(user_id=user_id, **kwargs)