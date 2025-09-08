from flask import Flask, Blueprint, jsonify, render_template, request, session
from app.services.pet import PetService
from app.services.dailycare.healthcare_service import HealthCareService
from app.services.dailycare.medicalcare_service import MedicalCareService
from app.models.dailycare.medicalCare.allergy import Allergy
from app.models.dailycare.medicalCare.disease import Disease
from app.models.dailycare.medicalCare.surgery import Surgery
from app.models.dailycare.medicalCare.vaccination import Vaccination
from app.models.dailycare.medicalCare.medication import Medication
from app.models import db
from app.services.dailycare.care_chatbot_service import CareChatbotService

import logging
from datetime import datetime,timedelta
from sqlalchemy import func

dailycare_api_bp = Blueprint('dailycare_api_bp', __name__)


# 모달 html렌더링
@dailycare_api_bp.route("/modal/<string:name>")
def load_modal(name):
    pet_id = request.args.get('pet_id')
    print('###### name :' , name ,'###### pet_id :' , pet_id) 
    return render_template(f"dailycare/dailycare_modal/{name}.html" , pet_id = pet_id)


logging.basicConfig(level=logging.INFO)

# 회원의 전체 펫 조회
@dailycare_api_bp.route("/get-pet/")
def get_my_pet():
    user_id = session.get('user_id')
    print(f'######## get-pet : {user_id}')

    pets = PetService.get_pets_by_user(user_id)
    
    if not pets:
        return jsonify({"error": "Pet이 존재하지 않습니다."})

    if isinstance(pets, list):
        result = [p.to_dict() for p in pets]
        print(result)
        return jsonify(result), 200
    
    return jsonify(pets.to_dict()), 200

@dailycare_api_bp.route('/pet-info/<pet_id>')
def get_pet_info(pet_id):
    pet = PetService.get_pet(pet_id)

    return jsonify(pet) , 200

# 개별 펫 조회
@dailycare_api_bp.route('/get-pet/<pet_id>')
def get_my_pet_by_user_id(pet_id):
    user_id = session.get('user_id')

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
    # Convert empty strings to None for numeric fields
    food = data.get('food')
    food = int(food) if food and food.strip() else None
    
    water = data.get('water') 
    water = float(water) if water and water.strip() else None
    
    weight_kg = data.get('weight_kg')
    weight_kg = float(weight_kg) if weight_kg and weight_kg.strip() else None
    
    walk_time_minutes = data.get('walk_time_minutes')
    walk_time_minutes = int(walk_time_minutes) if walk_time_minutes and walk_time_minutes.strip() else None
    
    record = HealthCareService.create_health_record(
        pet_id=pet_id,
        food=food,
        water=water,
        excrement_status=data.get('excrement_status'),
        weight_kg=weight_kg,
        walk_time_minutes=walk_time_minutes,
    )
    
    if not record:
        return jsonify({"success": False, "message": "기록이 이미 존재합니다."}), 200

    # 2. Medication 연결 (여러 개 가능)
    medication_ids = data.get('medication_ids') or []
    if medication_ids:
        HealthCareService.link_medications(record.care_id, medication_ids)

    # record 정보와 success 플래그를 함께 반환
    return jsonify({
        "success": True,
        "data": record.to_dict()
    }), 201


# 수정
@dailycare_api_bp.route('/update/healthcare/<care_id>', methods=['PUT'])
def update_healthcare(care_id):
    data = request.json

    record = HealthCareService.update_health_record(
        care_id=care_id,
        food=int(data['food']) if data.get('food') not in (None, "") else None,
        water=float(data['water']) if data.get('water') not in (None, "") else None,
        excrement_status=data.get('excrement_status'),
        weight_kg=float(data['weight_kg']) if data.get('weight_kg') not in (None, "") else None,
        walk_time_minutes=int(data['walk_time_minutes']) if data.get('walk_time_minutes') not in (None, "") else None,
        medication_ids=data.get('medication_ids') or []   # ✅ 새로 반영
    )

    if not record:
        return jsonify({"message": "해당 기록을 찾을 수 없습니다."}), 404

    return jsonify(record.to_dict()), 200



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
    meds = MedicalCareService.get_medications_by_pet(pet_id)
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
    
    record = MedicalCareService.create_allergy(
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
    allergies = MedicalCareService.get_allergy_pet(pet_id)
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
    
    record = MedicalCareService.create_disease(
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
    diseases = MedicalCareService.get_disease_pet(pet_id)
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
    
    record = MedicalCareService.create_surgery(
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
    surgeries = MedicalCareService.get_surgery_pet(pet_id)
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
    
    record = MedicalCareService.create_vaccination(
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
    vaccinations = MedicalCareService.get_vaccination_pet(pet_id)
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
    
    record = MedicalCareService.create_medication(
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

# medication 수정
@dailycare_api_bp.route('/medication/<int:medication_id>', methods=['PUT'])
def update_medication(medication_id):
    data = request.json
    medication = Medication.query.get(medication_id)
    
    medication.medication_name = data.get('medication_name', medication.medication_name)
    medication.purpose = data.get('purpose', medication.purpose)
    medication.dosage = data.get('dosage', medication.dosage)
    medication.frequency = data.get('frequency', medication.frequency)
    medication.side_effects_notes = data.get('side_effects_notes', medication.side_effects_notes)
    medication.hospital_name = data.get('hospital_name', medication.hospital_name)
    
    # 시작 날짜
    if data.get('start_date'):
        medication.start_date = datetime.strptime(data.get('start_date'), "%Y-%m-%d").date()
    # 끝? 날짜
    if data.get('end_date'):
        medication.end_date = datetime.strptime(data.get('end_date'), "%Y-%m-%d").date()
    
    db.session.commit()
    return jsonify(medication.to_dict()), 200

#  medication 삭제
@dailycare_api_bp.route('/medication/<int:medication_id>', methods=['DELETE'])
def delete_medication(medication_id):
    medication = Medication.query.get(medication_id)
    
    db.session.delete(medication)
    db.session.commit()
    return jsonify({"message": "삭제완료"}), 200

@dailycare_api_bp.route('/todo/')
def get_todo():
    user_id = session.get('user_id')
    print(f'\n\n\n\ngetTodo : {user_id}')
    todos= HealthCareService.get_todo_records_by_user_limit3(user_id)
    todo_list = [t.to_dict() for t in todos]
    return jsonify(todo_list), 200

@dailycare_api_bp.route('/todo/all/')
def get_all_todo():
    user_id = session.get('user_id')

    todos= HealthCareService.get_todo_records_by_user(user_id)
    todo_list = [t.to_dict() for t in todos]
    return jsonify(todo_list), 200


@dailycare_api_bp.route('/save/todo/', methods = ['POST'])
def save_todo():
    data = request.json
    todo_date_str = data.get("todo_date")  # '2025-08-16'
    todo_date = datetime.strptime(todo_date_str, "%Y-%m-%d").date() if todo_date_str else None
    record = HealthCareService.create_todo_record(
    
    user_id = session.get('user_id'),
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
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'Authentication required'}), 401
    
    data = request.get_json()
    user_input = data.get('message')
    pet_id = data.get('pet_id')
    
    if not user_input:
        return jsonify({'error' : 'message is required'}) , 400
    
    answer = CareChatbotService.chatbot_with_records(user_input, pet_id, user_id) # user_id는 왜 들어감..?
    result = CareChatbotService.pretty_format(answer)
    return jsonify({
        'user_input' : user_input,
        'response' : result
    })
    
@dailycare_api_bp.route('/health-chart/<int:pet_id>')
def get_health_chart_data(pet_id):
    days = request.args.get('days', 7, type=int)  # 기본 7일
    
    # 날짜 계산
    start_date = datetime.now() - timedelta(days=days)
    
    # 건강 기록 조회
    records = HealthCareService.get_health_records(
        pet_id, start_date, datetime.now()
    )
    
    # 차트용 데이터 형식으로 변환
    chart_data = {
        'dates': [],
        'weight': [],
        'food': [],
        'water': [],
        'exercise': []
    }
    
    for record in records:
        date_str = record.created_at.strftime('%Y-%m-%d')
        chart_data['dates'].append(date_str)
        
        # 데이터 추가
        chart_data['weight'].append(float(record.weight_kg) if record.weight_kg else 0)
        chart_data['food'].append(record.food if record.food else 0)
        chart_data['water'].append(float(record.water) if record.water else 0)
        chart_data['exercise'].append(record.walk_time_minutes if record.walk_time_minutes else 0)
    
    return jsonify(chart_data), 200

# 건강 데이터 요약 통계 
@dailycare_api_bp.route('/health-summary/<int:pet_id>')
def get_health_summary(pet_id):
    days = request.args.get('days', 7, type=int)
    start_date = datetime.now() - timedelta(days=days)
    
    records = HealthCareService.get_health_records(
        pet_id, start_date, datetime.now()
    )
    
    if not records:
        return jsonify({
            'total_records': 0,
            'avg_weight': 0,
            'avg_food': 0,
            'avg_water': 0,
            'avg_exercise': 0
        }), 200
    
    # 평균 계산
    total_records = len(records)
    weights = [r.weight_kg for r in records if r.weight_kg]
    foods = [r.food for r in records if r.food]
    waters = [r.water for r in records if r.water]
    exercises = [r.walk_time_minutes for r in records if r.walk_time_minutes]
    
    summary = {
        'total_records': total_records,
        'avg_weight': round(sum(weights) / len(weights), 2) if weights else 0,
        'avg_food': round(sum(foods) / len(foods), 1) if foods else 0,
        'avg_water': round(sum(waters) / len(waters), 1) if waters else 0,
        'avg_exercise': round(sum(exercises) / len(exercises), 1) if exercises else 0,
        'period_days': days
    }
    
    return jsonify(summary), 200

    


    