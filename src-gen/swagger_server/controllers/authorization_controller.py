from typing import List
"""
controller generated to handled auth operation described at:
https://connexion.readthedocs.io/en/latest/security.html
"""
from swagger_server.server_impl.checkBearerAuth import check_BearerAuth_impl
def check_BearerAuth(token):
    return check_BearerAuth_impl(token)


