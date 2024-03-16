#!/usr/bin/env python3

import connexion
from swagger_server import encoder
from flask_jwt_extended import JWTManager

from swagger_server.server_impl.endpoints import main_bp
from swagger_server.server_impl.db_config import db, insert_initial_values

import os

def main():
    env_variables = ['JWT_SECRET_KEY', 'SECRET_KEY', 'DASHBOARD_USERNAME', "DASHBOARD_PASSWORD"]
    # Check if the environment variables are set:
    missing_env_vars = [var for var in env_variables if os.getenv(var) is None]
    if missing_env_vars: raise EnvironmentError(f"Environment variables not set: {', '.join(missing_env_vars)}")

    app = connexion.App(__name__, specification_dir='./swagger/', server_args={'static_folder':'frontend/static'})
    app.app.json_encoder = encoder.JSONEncoder
    app.add_api('swagger.yaml', arguments={'title': 'kb-indexer API'}, pythonic_params=True)

    app.app.config['JWT_SECRET_KEY'] =  os.getenv('JWT_SECRET_KEY')
    app.app.secret_key = secret_key =  os.getenv('SECRET_KEY')
    jwt = JWTManager(app.app)
    insert_initial_values(db)
    app.app.register_blueprint(main_bp)

    app.run(port=8080)


if __name__ == '__main__':
    main()
