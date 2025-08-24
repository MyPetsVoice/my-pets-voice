from flask import Flask, Blueprint, jsonify, render_template, request
from app.services.pet_service import PetService
from app.services.dailycare.healthcare_service import HealthCareService
from app.services.dailycare.medicalcare_service import MedicationService
import logging

dailycare_api_bp = Blueprint('dailycare_api_bp', __name__, url_prefix= '/api/dailycares')


# 모달 html렌더링
@dailycare_api_bp.route("/modal/<string:name>")
def load_modal(name):
    print('###### name :' , name) 
    return render_template(f"dailycare/dailycare_modal/{name}.html")


logging.basicConfig(level=logging.INFO)

# 회원의 전체 펫 조회
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

# 개별 펫 조회
@dailycare_api_bp.route('/get-pet/<user_id>/<pet_id>')
def get_my_pet_by_user_id(user_id,pet_id):
    print(f'입력된 petId : {pet_id} userId {user_id}')
    pets = PetService.get_pet_by_id(pet_id, user_id)
    print(pets)
    if not pets:
        return jsonify({"error": "Pet not found"}), 404

    
    return jsonify(pets.to_dict()), 200

# HealtCare 생성
@dailycare_api_bp.route('/save/healthcare/<pet_id>', methods = ['POST'])
def save_healthcare(pet_id):
    data = request.json
    record = HealthCareService.create_health_record(
        pet_id=pet_id,
        food=data.get('food'),
        water=data.get('water'),
        excrement_status=data.get('excrement_status'),
        weight_kg=data.get('weight_kg'),
        walk_time_minutes=data.get('walk_time_minutes'),
    )
     # 2. Medication 연결 (여러 개 가능)
    medication_ids = data.get('medication_ids', [])
    HealthCareService.link_medications(record.care_id, medication_ids)
    return jsonify(record.to_dict()), 201

#Healthcare조회
@dailycare_api_bp.route('/healthcare/<pet_id>' )
def get_health_log(pet_id):
    log = HealthCareService.get_health_records_by_pet(pet_id)
    if isinstance(log, list):
        return jsonify([l.to_dict() for l in log]), 200
    else:
        return jsonify(log.to_dict()), 200


# HealthCare 단일 조회
@dailycare_api_bp.route('/healthcare/<int:pet_id>/<int:care_id>', methods=['GET'])
def get_health_record(pet_id, care_id):
    record = HealthCareService.get_health_record_by_id(care_id, pet_id)
    if not record:
        return jsonify({"error": "Health record not found"}), 404
    return jsonify(record.to_dict()), 200

# Medication 조회
@dailycare_api_bp.route('/medications/<int:pet_id>', methods=['GET'])
def get_medications(pet_id):
    meds = MedicationService.get_medications_by_pet(pet_id)
    return jsonify([m.to_dict() for m in meds]), 200

@dailycare_api_bp.route('/get-healthcare/<int:care_id>', methods=['GET'])
def get_healthcare(care_id):
    record = HealthCareService.get_health_record_by_id(care_id)
    if not record:
        return jsonify({"error": "Record not found"}), 404

    # 연결된 Medication 포함
    meds = [
        {
            "medication_id": link.medication.medication_id,
            "name": link.medication.medication_name,
            "dosage": link.medication.dosage,
            "frequency": link.medication.frequency
        }
        for link in record.medication_links
    ]

    result = record.to_dict()
    result['medications'] = meds

    return jsonify(result), 200
