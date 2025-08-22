from flask import Flask, Blueprint, jsonify, render_template

dailycare_api_bp = Blueprint('dailycare_api_bp', __name__, url_prefix= '/api/dailycares')