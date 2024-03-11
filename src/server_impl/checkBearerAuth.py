from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity
from connexion.exceptions import OAuthProblem

def check_BearerAuth_impl(token):
    try:
        # Flask-JWT-Extended's function to verify the JWT present in the current request
        verify_jwt_in_request()
        #  get the user's identity from the JWT
        user_identity = get_jwt_identity()
        # return True
        # If verification succeeds the user object
        return {'user': user_identity}
    except Exception as e:
        raise OAuthProblem('Invalid token: ' + str(e))