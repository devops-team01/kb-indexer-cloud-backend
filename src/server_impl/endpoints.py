from flask import Blueprint, send_from_directory, session, redirect, url_for

from flask import Blueprint, request, jsonify, make_response, current_app
from flask_jwt_extended import create_access_token

import os
# from werkzeug.security import check_password_hash

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def root():
    if 'logged_in' not in session: 
        return redirect(url_for("main.login"))
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
        session["logged_in"] = True
        access_token = create_access_token(identity=username)
        return jsonify(access_token=access_token), 200
    else:
        return make_response('Invalid username or password', 401)