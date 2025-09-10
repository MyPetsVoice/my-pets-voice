from flask import Blueprint, render_template, redirect, url_for, request, session
from app.services.dailycare.healthcare_service import HealthCareService

dailycare_views_bp = Blueprint('dailycare_views', __name__)

# 데일리케어페이지
@dailycare_views_bp.route('/', methods=['GET'])
def get_dailycare():
    if 'user_id' not in session:
        return redirect(url_for('index'))
    
    user = session.get('user')
    user_nickname = user['kakao_account']['profile']['nickname']

    return render_template('dailycare/dailycare.html', user=user_nickname)

# 건강분석 페이지
@dailycare_views_bp.route('/analysis')
def get_analysis():
    if 'user_id' not in session:
        return redirect(url_for('index'))
    
    user = session.get('user')
    user_nickname = user['kakao_account']['profile']['nickname']

    return render_template('dailycare/analysis_pet.html', user=user_nickname)

# 의료기록 모아보기 ('전체기록')
@dailycare_views_bp.route('/medication-history/<int:pet_id>')
def get_medication_history(pet_id):
    if 'user_id' not in session:
            return redirect(url_for('index'))
    
    user = session.get('user')
    user_nickname = user['kakao_account']['profile']['nickname']

    return render_template('dailycare/medication_history.html', pet_id=pet_id, user=user_nickname)

from datetime import datetime, timedelta, timezone

KST = timezone(timedelta(hours=9))

# 건강기록 모아보기 ('기록보기')
@dailycare_views_bp.route('/health-history')
def get_healthcare_history():
    if 'user_id' not in session:
        return redirect(url_for('index'))

    user = session.get('user')
    user_nickname = user['kakao_account']['profile']['nickname']

    care_id = request.args.get('care_id')  # URL에서 ?care_id=값 가져오기
    if care_id:
        record = HealthCareService.get_health_record_by_id(care_id)
        medication = HealthCareService.get_linked_medications(care_id) or []

        # ✅ updated_at 포맷팅 (한국시간 변환 + 보기 좋은 문자열)
        if hasattr(record, "updated_at") and isinstance(record.updated_at, datetime):
            if record.updated_at.tzinfo is None:
                record.updated_at = record.updated_at.replace(tzinfo=timezone.utc)
        record.updated_at = record.updated_at.astimezone(KST).strftime("%Y-%m-%d %H:%M:%S")

        return render_template(
            'dailycare/healthcare_detail.html', record=record, medication=medication, user=user_nickname
        )
    else:
        return render_template('dailycare/healthcare_history.html', user=user_nickname)

@dailycare_views_bp.route('/update/health-care')
def getUpdateHealthcare():
    if 'user_id' not in session:
        return redirect(url_for('index'))

    user = session.get('user')
    user_nickname = user['kakao_account']['profile']['nickname']
    care_id = request.args.get('care_id')
    return render_template('dailycare/healthcare_edit.html', care_id = care_id, user=user_nickname)


# Todo 전체 리스트
@dailycare_views_bp.route('/todo')
def get_todo():
    if 'user_id' not in session:
        return redirect(url_for('index'))
    
    user = session.get('user')
    user_nickname = user['kakao_account']['profile']['nickname']

    todo_id = request.args.get('todo_id')
    print(todo_id)
    if todo_id:
        record = HealthCareService.get_todo_record_by_id(todo_id)
        print(record)
        return render_template('dailycare/todo_detail.html', todo = record, user=user_nickname)
    else:
        return render_template('dailycare/todo_history.html', user=user_nickname)
    
@dailycare_views_bp.route('/update/todo')
def editTodo():
    if 'user_id' not in session:
        return redirect(url_for('index'))
    
    user = session.get('user')
    user_nickname = user['kakao_account']['profile']['nickname']

    todo_id = request.args.get('todo_id')
    record = HealthCareService.get_todo_record_by_id(todo_id)
    return render_template('dailycare/todo_edit.html', todo_id = todo_id, todo = record, user=user_nickname)

# 건강상태 리포트
@dailycare_views_bp.route('/health-chart')
def get_health_chart():
    if 'user_id' not in session:
        return redirect(url_for('index'))

    user = session.get('user')
    user_nickname = user['kakao_account']['profile']['nickname']
    return render_template('dailycare/health_chart.html', user=user_nickname)