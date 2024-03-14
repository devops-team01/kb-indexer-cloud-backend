#!/usr/bin/env python3

import connexion
from swagger_server import encoder
from flask_jwt_extended import JWTManager

from swagger_server.server_impl.endpoints import main_bp
from swagger_server.server_impl.db_config import db, insert_initial_values

def main():
    app = connexion.App(__name__,
                        specification_dir='./swagger/',
                        server_args={
                        "static_url_path":'', 
                        "static_folder":'./frontend/'})
    app.app.json_encoder = encoder.JSONEncoder
    app.add_api('swagger.yaml', arguments={'title': 'kb-indexer API'}, pythonic_params=True)
    
    app.app.config['JWT_SECRET_KEY'] = "super-secret"  # Change this!
    app.app.secret_key = "super-secret"  # Change this!
    jwt = JWTManager(app.app)
    insert_initial_values(db)
    app.app.register_blueprint(main_bp)
    app.run(port=8080)


if __name__ == '__main__':
    main()
