from flask import Flask, Blueprint, jsonify, render_template, request
from app.services.pet_service import PetService
from app.services.dailycare.healthcare_service import HealthCareService
from app.services.dailycare.medicalcare_service import MedicationService
from app.services.dailycare.care_chatbot_service import careChatbotService

import logging
from datetime import datetime

dailycare_api_bp = Blueprint('dailycare_api_bp', __name__, url_prefix= '/api/dailycares')


# 모달 html렌더링
@dailycare_api_bp.route("/modal/<string:name>")
def load_modal(name):
    pet_id = request.args.get('pet_id')
    print('###### name :' , name ,'###### pet_id :' , pet_id) 
    return render_template(f"dailycare/dailycare_modal/{name}.html" , pet_id = pet_id)


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

@dailycare_api_bp.route('/pet-info/<pet_id>')
def get_pet_info(pet_id):
    pet = PetService.get_pet(pet_id)
    return jsonify(pet.to_dict()) , 200

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
    medication_ids = data.get('medication_ids') or []
    if medication_ids:
        HealthCareService.link_medications(record.care_id, medication_ids)
        
    return jsonify(record.to_dict()), 201

@dailycare_api_bp.route('/update/healthcare/<int:care_id>', methods=['PUT'])
def update_healthcare(care_id):
    data = request.get_json() or {}
    # 중복 방지: data에 care_id가 있으면 제거
    data.pop('care_id', None)

    updated_record = HealthCareService.update_health_record(care_id, **data)
    
    if updated_record is None:
        return jsonify({"error": "healthcare record not found"}), 404

    # updated_record가 dict이면 그대로 반환, 아니면 to_dict 호출
    if isinstance(updated_record, dict):
        return jsonify(updated_record), 200
    elif hasattr(updated_record, 'to_dict'):
        return jsonify(updated_record.to_dict()), 200
    else:
        return jsonify({"error": "updated record has invalid type"}), 500



@dailycare_api_bp.route('/delete/healthcare/<int:care_id>', methods=['DELETE'])
def delete_healthcare(care_id):
    """특정 care_id 기록 삭제"""
    record_deleted = HealthCareService.delete_health_record(care_id)
    if not record_deleted:
        return jsonify({"error": "Health record not found"}), 404
    return jsonify({"message": "Health record deleted successfully"}), 200

#Healthcare조회
@dailycare_api_bp.route('/healthcare/pet/<pet_id>' )
def get_health_log(pet_id):
    log = HealthCareService.get_health_records_by_pet(pet_id)
    print('###### log : ', log)
    if isinstance(log, list):
        return jsonify([l.to_dict() for l in log]), 200
    else:
        return jsonify(log.to_dict()), 200


# HealthCare 단일 조회
@dailycare_api_bp.route('/healthcare/<int:care_id>', methods=['GET'])
def get_health_record( care_id):
    record = HealthCareService.get_health_record_by_id(care_id)
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
    print(f'##### meds : {meds}')

    result = record.to_dict()
    result['medications'] = meds

    return jsonify(result), 200

@dailycare_api_bp.route('/save/allergy/<pet_id>', methods = ['POST'])
def saveAllergy(pet_id):
    data = request.json
    record = MedicationService.create_medication(
        pet_id = pet_id,
        allergy_type = data.get('allergy_type'),
        allergen = data.get('allergen'),
        symptoms = data.get('symptoms'),
        severity = data.get('severity')
    )
    
    return jsonify(record.to_dict()),200

@dailycare_api_bp.route('/save/medication/<pet_id>', methods = ['POST'])
def save_medication(pet_id):
    data = request.json
    start_date_str = request.json.get("start_date")  # '2025-08-19'
    end_date_str = request.json.get("end_date")      # '2025-08-22'

    start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date() if start_date_str else None
    end_date = datetime.strptime(end_date_str, "%Y-%m-%d").date() if end_date_str else None
    
    record = MedicationService.create_medication(
    pet_id = pet_id,
    medication_name = data.get('medication_name'),
    purpose = data.get('purpose'),
    dosage = data.get('dosage'),
    frequency = data.get('frequency'),
    end_date = end_date,
    start_date = start_date,
    side_effects_notes = data.get('side_effects_notes'),
    hospital_name = data.get('hospital_name')
    )
    
    return jsonify(record.to_dict()), 200

@dailycare_api_bp.route('/todo/<user_id>')
def get_todo(user_id):
    todos= HealthCareService.get_todo_records_by_user_limit3(user_id)
    todo_list = [t.to_dict() for t in todos]
    return jsonify(todo_list), 200

@dailycare_api_bp.route('/todo/all/<user_id>')
def get_all_todo(user_id):
    todos= HealthCareService.get_todo_records_by_user(user_id)
    todo_list = [t.to_dict() for t in todos]
    return jsonify(todo_list), 200


@dailycare_api_bp.route('/save/todo/<user_id>', methods = ['POST'])
def save_todo(user_id):
    data = request.json
    todo_date_str = data.get("todo_date")  # '2025-08-16'
    todo_date = datetime.strptime(todo_date_str, "%Y-%m-%d").date() if todo_date_str else None
    record = HealthCareService.create_todo_record(
    
    user_id = user_id,
    todo_date = todo_date,
    title = data.get('title'),
    description = data.get('description'),
    status = data.get('status'),
    priority = data.get('priority'),
   
    )
    
    return jsonify(record.to_dict()), 200

@dailycare_api_bp.route('/todo/<todo_id>', methods=['PUT'])
def updateTodo(todo_id):
  print(todo_id)
  data = request.get_json()
  if not data:
      return jsonify({'message' : '잘못된 요청입니다'}), 400
  print('\n\n\n#### input Data : ' , data)
  HealthCareService.update_todo_record(todo_id, **data)
  return jsonify('성공'),200
  
@dailycare_api_bp.route('/todo/<todo_id>', methods= ['DELETE'])
def deleteTodo(todo_id):
    data = HealthCareService.delete_todo_record(todo_id)
    if not data:
        return jsonify({"error": "Health record not found"}), 404
    return jsonify({"message": "Todo record deleted successfully"}), 200

@dailycare_api_bp.route('/care-chatbot' , methods = ['POST'])
def ask_chatbot():
    """careChatbot Service"""
    data = request.get_json()
    user_input = data.get('message')
    pet_id = data.get('pet_id' , 1)
    user_id = data.get('user_id' , 1)
    
    if not user_input:
        return jsonify({'error' : 'message is required'}) , 400
    
    answer = careChatbotService.chatbot_with_records(user_input, pet_id, user_id)
    return jsonify({
        'user_input' : user_input,
        'response' : answer
    })

    


    