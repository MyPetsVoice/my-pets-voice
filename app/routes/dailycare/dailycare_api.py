from flask import Flask, Blueprint, jsonify, render_template

dailycare_api_bp = Blueprint('dailycare_api_bp', __name__, url_prefix= '/api/dailycares')


# 모달 html렌더링
@dailycare_api_bp.route("/modal/<string:name>")
def load_modal(name):
    print('###### name :' , name) 
    return render_template(f"dailycare/dailycare_modal/{name}.html")
