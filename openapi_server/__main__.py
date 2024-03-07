#!/usr/bin/env python3

import os
import connexion
from openapi_server import encoder

from pymongo import MongoClient
# from flask_socketio import SocketIO
from flask import send_from_directory, request, Response
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Set from hidden .env file
USERNAME = os.getenv("USERNAME")
PASSWORD = os.getenv("PASSWORD")

def check_auth(username, password):
    return username == USERNAME and password == PASSWORD

def authenticate():
    return Response(
    'Incorrect credentials', 401,
    {'WWW-Authenticate': 'Basic realm="Login Required"'})

def requires_auth(f):
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            return authenticate()
        return f(*args, **kwargs)
    return decorated

def main():
    app = connexion.App(__name__, specification_dir='./openapi/')
    app.app.json_encoder = encoder.JSONEncoder
    app.add_api('openapi.yaml', arguments={'title': 'kb-indexer API'}, pythonic_params=True)
    
    @app.route('/')
    @requires_auth
    def root():
        return send_from_directory('./frontend', 'index.html')
    
    app.run(port=8080)

if __name__ == '__main__':
    main()
