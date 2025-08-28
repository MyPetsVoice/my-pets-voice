from flask import Flask, Blueprint, jsonify, render_template, request
from app.services.pet_service import PetService
from app.services.dailycare.healthcare_service import HealthCareService
from app.services.dailycare.medicalcare_service import MedicationService
from app.models.dailycare.medicalCare.allergy import Allergy
from app.models.dailycare.medicalCare.disease import Disease
from app.models.dailycare.medicalCare.surgery import Surgery
from app.models.dailycare.medicalCare.vaccination import Vaccination
from app.models.dailycare.medicalCare.medication import Medication
from app.models import db

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
    print(f'##### meds : {meds}')

    result = record.to_dict()
    result['medications'] = meds

    return jsonify(result), 200

@dailycare_api_bp.route('/save/allergy/<pet_id>', methods = ['POST'])
def saveAllergy(pet_id):
    data = request.json
    
    record = MedicationService.create_allergy(
        pet_id = pet_id,
        allergy_type = data.get('allergy_type'),
        allergen = data.get('allergen'),
        symptoms = data.get('symptoms'),
        severity = data.get('severity')
    )
    
    return jsonify(record.to_dict()),200

# 알러지 정보 조회
@dailycare_api_bp.route('/allergy/<int:pet_id>',methods=['GET'])
def get_allergy(pet_id):
    allergies = MedicationService.get_allergy_pet(pet_id)
    return jsonify([allergy.to_dict() for allergy in allergies]), 200

# 알러지 정보 수정
@dailycare_api_bp.route('/allergy/<int:allergy_id>', methods=['PUT'])
def update_allergy(allergy_id):
    data = request.json
    allergy = Allergy.query.get(allergy_id)
    
    allergy.allergy_type = data.get('allergy_type', allergy.allergy_type)
    allergy.allergen = data.get('allergen', allergy.allergen)
    allergy.symptoms = data.get('symptoms', allergy.symptoms)
    allergy.severity = data.get('severity', allergy.severity)
    
    db.session.commit()
    return jsonify(allergy.to_dict()), 200

# 알러지 정보 삭제
@dailycare_api_bp.route('/allergy/<int:allergy_id>', methods=['DELETE'])
def delete_allergy(allergy_id):
    allergy = Allergy.query.get(allergy_id)
    db.session.delete(allergy)
    db.session.commit()
    return jsonify({"message": "삭제완료"}), 200

#----------------------------------------------------------------------

# 질병 이력 생성
@dailycare_api_bp.route('/save/disease/<int:pet_id>', methods=['POST'])
def save_disease(pet_id):
    data = request.json
    
    diagnosis_date = data.get('diagnosis_date')
    if diagnosis_date:
        diagnosis_date = datetime.strptime(diagnosis_date, "%Y-%m-%d").date()
    
    record = MedicationService.create_disease(
        pet_id=pet_id,
        disease_name=data.get('disease_name'),
        symptoms=data.get('symptoms'),
        treatment_details=data.get('treatment_details'),
        hospital_name=data.get('hospital_name'),
        doctor_name=data.get('doctor_name'),
        medical_cost=data.get('medical_cost'),
        diagnosis_date=diagnosis_date
    )
    
    return jsonify(record.to_dict()), 200

# 질병 이력 목록 조회
@dailycare_api_bp.route('/diseases/<int:pet_id>', methods=['GET'])
def get_diseases(pet_id):
    diseases = MedicationService.get_disease_pet(pet_id)
    return jsonify([disease.to_dict() for disease in diseases]), 200

# 질병 이력 수정
@dailycare_api_bp.route('/disease/<int:disease_id>', methods=['PUT'])
def update_disease(disease_id):
    data = request.json
    disease = Disease.query.get(disease_id)
    
    disease.disease_name = data.get('disease_name', disease.disease_name)
    disease.symptoms = data.get('symptoms', disease.symptoms)
    disease.treatment_details = data.get('treatment_details', disease.treatment_details)
    disease.hospital_name = data.get('hospital_name', disease.hospital_name)
    disease.medical_cost = data.get('medical_cost', disease.medical_cost)
    
    if data.get('diagnosis_date'):
        disease.diagnosis_date = datetime.strptime(data.get('diagnosis_date'), "%Y-%m-%d").date()
    
    db.session.commit()
    return jsonify(disease.to_dict()), 200

# 질병 이력 삭제
@dailycare_api_bp.route('/disease/<int:disease_id>', methods=['DELETE'])
def delete_disease(disease_id):
    disease = Disease.query.get(disease_id)
    db.session.delete(disease)
    db.session.commit()
    return jsonify({"message": "삭제완료"}), 200

#-----------------------------------------------------------------------

# 수술 이력 생성
@dailycare_api_bp.route('/save/surgery/<int:pet_id>', methods=['POST'])
def save_surgery(pet_id):
    data = request.json
    
    surgery_date = datetime.strptime(data.get('surgery_date'), "%Y-%m-%d").date()
    
    record = MedicationService.create_surgery(
        pet_id=pet_id,
        surgery_name=data.get('surgery_name'),
        surgery_date=surgery_date,
        surgery_summary=data.get('surgery_summary'),
        hospital_name=data.get('hospital_name'),
        doctor_name=data.get('doctor_name'),
        recovery_status=data.get('recovery_status')
    )
    
    return jsonify(record.to_dict()), 200

# 수술 목록 조회
@dailycare_api_bp.route('/surgeries/<int:pet_id>', methods=['GET'])
def get_surgeries(pet_id):
    surgeries = MedicationService.get_surgery_pet(pet_id)
    return jsonify([surgery.to_dict() for surgery in surgeries]), 200

# 수술 수정
@dailycare_api_bp.route('/surgery/<int:surgery_id>', methods=['PUT'])
def update_surgery(surgery_id):
    data = request.json
    surgery = Surgery.query.get(surgery_id)
    
    surgery.surgery_name = data.get('surgery_name', surgery.surgery_name)
    surgery.surgery_summary = data.get('surgery_summary', surgery.surgery_summary)
    surgery.hospital_name = data.get('hospital_name', surgery.hospital_name)
    surgery.recovery_status = data.get('recovery_status', surgery.recovery_status)
    
    if data.get('surgery_date'):
        surgery.surgery_date = datetime.strptime(data.get('surgery_date'), "%Y-%m-%d").date()
    
    db.session.commit()
    return jsonify(surgery.to_dict()), 200

# 수술 이력 삭제
@dailycare_api_bp.route('/surgery/<int:surgery_id>', methods=['DELETE'])
def delete_surgery(surgery_id):
    surgery = Surgery.query.get(surgery_id)
    db.session.delete(surgery)
    db.session.commit()
    return jsonify({"message": "삭제완료"}), 200

# 예방접종 생성
@dailycare_api_bp.route('/save/vaccination/<int:pet_id>', methods=['POST'])
def save_vaccination(pet_id):
    data = request.json
    
    vaccination_date = datetime.strptime(data.get('vaccination_date'), "%Y-%m-%d").date()
    next_vaccination_date = None
    if data.get('next_vaccination_date'):
        next_vaccination_date = datetime.strptime(data.get('next_vaccination_date'), "%Y-%m-%d").date()
    
    record = MedicationService.create_vaccination(
        pet_id=pet_id,
        vaccine_name=data.get('vaccine_name'),
        vaccination_date=vaccination_date,
        side_effects=data.get('side_effects'),
        hospital_name=data.get('hospital_name'),
        next_vaccination_date=next_vaccination_date,
        manufacturer=data.get('manufacturer'),  
        lot_number=data.get('lot_number'),
    )
    
    return jsonify(record.to_dict()), 200

# 예방접종 목록 조회
@dailycare_api_bp.route('/vaccinations/<int:pet_id>', methods=['GET'])
def get_vaccinations(pet_id):
    vaccinations = MedicationService.get_vaccination_pet(pet_id)
    return jsonify([vaccination.to_dict() for vaccination in vaccinations]), 200

# 예방접종 수정
@dailycare_api_bp.route('/vaccination/<int:vaccination_id>', methods=['PUT'])
def update_vaccination(vaccination_id):
    data = request.json
    vaccination = Vaccination.query.get(vaccination_id)
    
    vaccination.vaccine_name = data.get('vaccine_name', vaccination.vaccine_name)
    vaccination.side_effects = data.get('side_effects', vaccination.side_effects)
    vaccination.hospital_name = data.get('hospital_name', vaccination.hospital_name)
    
    if data.get('vaccination_date'):
        vaccination.vaccination_date = datetime.strptime(data.get('vaccination_date'), "%Y-%m-%d").date()
    
    if data.get('next_vaccination_date'):
        vaccination.next_vaccination_date = datetime.strptime(data.get('next_vaccination_date'), "%Y-%m-%d").date()
    
    db.session.commit()
    return jsonify(vaccination.to_dict()), 200

# 예방접종 삭제
@dailycare_api_bp.route('/vaccination/<int:vaccination_id>', methods=['DELETE'])
def delete_vaccination(vaccination_id):
    vaccination = Vaccination.query.get(vaccination_id)
    db.session.delete(vaccination)
    db.session.commit()
    return jsonify({"message": "삭제완료"}), 200


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

@dailycare_api_bp.route('/save/todo/<user_id>', methods = ['POST'])
def save_todo(user_id):
    data = request.json
    record = HealthCareService.create_todo_record(
    
    user_id = user_id,
    todo_date = data.get('todo_date'),
    title = data.get('title'),
    description = data.get('description'),
    status = data.get('status'),
    priority = data.get('priority'),
   
    )
    
    return jsonify(record.to_dict()), 200
    


