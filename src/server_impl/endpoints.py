from flask import Blueprint, send_from_directory, session, redirect
from flask import Blueprint, request, jsonify, make_response
from flask_jwt_extended import create_access_token, decode_token
from flask_jwt_extended.exceptions import JWTDecodeError, JWTExtendedException
import urllib.parse
# from werkzeug.security import check_password_hash

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def root():
    if 'logged_in' not in session: 
        return redirect(urllib.parse.urljoin(request.base_url, 'login'))
    else:
        # Check if the JWT token is still valid
        try:
            
            token = session.get('token')
            if token:
                decode_token(token)
                # If decoding succeeds, token is still valid
                return send_from_directory('./frontend', 'index.html')
            else:
                return redirect(urllib.parse.urljoin(request.base_url, 'login'))

        except (JWTDecodeError, JWTExtendedException):
            # If token is expired or invalid, clear the session and redirect to login
            session.clear()
            
            return redirect(urllib.parse.urljoin(request.base_url, 'login'))

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
        session["token"] = access_token
        return jsonify(access_token=access_token), 200
    else:
        return make_response('Invalid username or password', 401)