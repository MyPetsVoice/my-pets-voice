from flask import Blueprint, request, jsonify


api_chat_bp = Blueprint('api_chat', __name__)

@api_chat_bp.route('/')
def get_persona():

    pass