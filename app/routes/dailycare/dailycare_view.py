from flask import Flask, Blueprint, jsonify, render_template

dailycare_bp = Blueprint('dailycare_bp', __name__)
# 데일리케어페이지
@dailycare_bp.route('/', methods=['GET'])
def get_dailycare():
    return render_template('dailycare/dailycare.html')
# 건강분석 페이지
@dailycare_bp.route('/analysis')
def get_analysis():
    return render_template('dailycare/analysis_pet.html')
# 의료기록 모아보기 ('전체기록')
@dailycare_bp.route('/medication-history')
def get_medication_history():
    return render_template('dailycare/medication_history.html')

# 건강기록 모아보기 ('기록보기')
@dailycare_bp.route('/health-history')
def get_healthcare_history():
    return render_template('dailycare/healthcare_history.html')



