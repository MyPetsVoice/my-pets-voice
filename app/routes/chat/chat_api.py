from flask import Blueprint, request, jsonify


chat_api_bp = Blueprint('chat_api', __name__)

@chat_api_bp.route('/')
def get_persona():

    pass