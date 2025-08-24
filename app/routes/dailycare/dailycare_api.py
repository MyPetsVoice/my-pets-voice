from flask import Flask, Blueprint, jsonify, render_template
from app.services.pet_service import PetService


import logging

dailycare_api_bp = Blueprint('dailycare_api_bp', __name__, url_prefix= '/api/dailycares')


# 모달 html렌더링
@dailycare_api_bp.route("/modal/<string:name>")
def load_modal(name):
    print('###### name :' , name) 
    return render_template(f"dailycare/dailycare_modal/{name}.html")


logging.basicConfig(level=logging.INFO)

@dailycare_api_bp.route("/get-pet/<user_id>")
def get_my_pet(user_id):
    pets = PetService.get_pets_by_user(user_id)
    
    if not pets:
        return jsonify({"error": "Pet not found"}), 404

    if isinstance(pets, list):
        result = [p.to_dict() for p in pets]
        print(result)
        return jsonify(result), 200
    
    return jsonify(pets.to_dict()), 200

@dailycare_api_bp.route('/get-pet/<user_id>/<pet_id>')
def get_my_pet_by_user_id(user_id,pet_id):
    print(f'입력된 petId : {pet_id} userId {user_id}')
    pets = PetService.get_pet_by_id(pet_id, user_id)
    print(pets)
    if not pets:
        return jsonify({"error": "Pet not found"}), 404

    
    return jsonify(pets.to_dict()), 200

