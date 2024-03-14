from flask import Blueprint, send_from_directory, session, redirect, url_for

from flask import Blueprint, request, jsonify, make_response
from flask_jwt_extended import create_access_token
# from werkzeug.security import check_password_hash

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def root():
    if 'logged_in' not in session: 
        return redirect(url_for("main_bp.login"))
    return send_from_directory('./frontend', 'dashboard.html')

@main_bp.route('/login')
def show_login():
    return send_from_directory('./frontend', 'login.html')

@main_bp.route('/login', methods=['POST'])
def login():
    username = request.form.get('username')
    password = request.form.get('password')
    
    if username == password: 
        session["logged_in"] = True
        access_token = create_access_token(identity=username)
        return jsonify(access_token=access_token), 200
    else:
        return make_response('Invalid username or password', 401)