from flask import Flask, Blueprint, jsonify, render_template

dailycare_bp = Blueprint('dailycare_bp', __name__)

@dailycare_bp.route('/', methods=['GET'])
def get_dailycare():
    return render_template('dailycare/dailycare.html')

# 모달 전용 라우트
@dailycare_bp.route("/modal/<string:name>")
def load_modal(name):
    print('###### name :' , name)
    return render_template(f"dailycare/dailycare_modal/{name}.html")
    

