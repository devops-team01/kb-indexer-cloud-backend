from flask import Blueprint, send_from_directory, session, redirect

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def root():
    if 'logged_in' not in session: 
        return redirect('/login')
    return send_from_directory('./frontend', 'index.html')

@main_bp.route('/login')
def show_login():
    return send_from_directory('./frontend', 'login.html')