from datetime import datetime
from datetime import timedelta
from datetime import timezone

from flask import Blueprint, send_from_directory, session, redirect
from flask import request, jsonify, make_response, url_for
from flask_jwt_extended import jwt_required, create_access_token, decode_token, get_jwt, set_access_cookies, get_jwt_identity
from flask_jwt_extended.exceptions import JWTDecodeError, JWTExtendedException
import urllib.parse

import os
# from werkzeug.security import check_password_hash

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
@jwt_required()
def root():
    return send_from_directory('./frontend', 'dashboard.html')

@main_bp.route('/login')
def show_login():
    return send_from_directory('./frontend', 'login.html')

@main_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    # __main__.py asserts these are present 
    if username  == os.getenv('DASHBOARD_USERNAME') and password == os.getenv('DASHBOARD_PASSWORD'):
        #session["logged_in"] = True

        access_token = create_access_token(identity=username)
        set_access_cookies(response, access_token)
	response = jsonify(access_token=access_token)
	return response, 200
    else:
        return make_response('Invalid username or password', 401)
    
@main_bp.after_request
def refresh_expiring_jwts(response):
    try:
        exp_timestamp = get_jwt()["exp"]
        now = datetime.now(timezone.utc)
        target_timestamp = datetime.timestamp(now + timedelta(minutes=30))
        if target_timestamp > exp_timestamp:
            access_token = create_access_token(identity=get_jwt_identity())
            set_access_cookies(response, access_token)
        return response
    except (RuntimeError, KeyError):
        # Case where there is not a valid JWT. Just return the original response
        return response
