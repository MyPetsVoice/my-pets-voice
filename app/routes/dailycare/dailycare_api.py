from flask import Flask, Blueprint, jsonify, render_template
from app.services.pet_service import PetService

pet_api_bp = Blueprint('pet_api_bp', __name__, url_prefix="/api/pets")

dailycare_api_bp = Blueprint('dailycare_api_bp', __name__, url_prefix= '/api/dailycares')


# 모달 html렌더링
@dailycare_api_bp.route("/modal/<string:name>")
def load_modal(name):
    print('###### name :' , name) 
    return render_template(f"dailycare/dailycare_modal/{name}.html")

@dailycare_api_bp.route("/get-pet/<user_id>")
def get_my_pet(user_id):
    pet = PetService.get_pets_by_user(user_id)
    if not pet:
        return jsonify({"error": "Pet not found"}), 404
    return jsonify(pet)
    