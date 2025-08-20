from flask import Flask, Blueprint, jsonify, render_template

dailycare_bp = Blueprint('dailycare_bp', __name__)

@dailycare_bp.route('/dailycare', methods=['GET'])
def get_dailycare():
    return render_template('dailycare/dailycare.html')


