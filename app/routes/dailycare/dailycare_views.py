from flask import Blueprint, render_template, request
from app.services.dailycare.healthcare_service import HealthCareService

dailycare_views_bp = Blueprint('dailycare_views', __name__)

# 데일리케어페이지
@dailycare_views_bp.route('/', methods=['GET'])
def get_dailycare():
    current_user = 1 # 임시
    return render_template('dailycare/dailycare.html', user = current_user)

# 건강분석 페이지
@dailycare_views_bp.route('/analysis')
def get_analysis():
    return render_template('dailycare/analysis_pet.html')

# 의료기록 모아보기 ('전체기록')
@dailycare_views_bp.route('/medication-history/<int:pet_id>')
def get_medication_history(pet_id):
    return render_template('dailycare/medication_history.html', pet_id=pet_id)

# 건강기록 모아보기 ('기록보기')
@dailycare_views_bp.route('/health-history')
def get_healthcare_history():
    care_id = request.args.get('care_id')  # URL에서 ?care_id=값 가져오기
    if care_id:
        record = HealthCareService.get_health_record_by_id(care_id)
        medication = HealthCareService.get_linked_medications(care_id) or []
        return render_template(
            'dailycare/healthcare_detail.html', record =record, medication = medication
        )
    else:
        return render_template('dailycare/healthcare_history.html')

@dailycare_views_bp.route('/update/health-care')
def getUpdateHealthcare():
    care_id = request.args.get('care_id')
    return render_template('dailycare/healthcare_edit.html', care_id = care_id)


# Todo 전체 리스트
@dailycare_views_bp.route('/todo')
def get_todo():
    current_user = 1 #임시 나중에 로그인한 user가져오는 거 할거임
    todo_id = request.args.get('todo_id')
    print(todo_id)
    if todo_id:
        record = HealthCareService.get_todo_record_by_id(todo_id)
        print(record)
        return render_template('dailycare/todo_detail.html', todo = record)
    else:
        return render_template('dailycare/todo_history.html', user = current_user )
    
@dailycare_views_bp.route('/update/todo')
def editTodo():
    todo_id = request.args.get('todo_id')
    print(todo_id)
    record = HealthCareService.get_todo_record_by_id(todo_id)
    print(record)
    return render_template('dailycare/todo_edit.html', todo_id = todo_id, todo = record)