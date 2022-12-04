from flask_httpauth import MultiAuth

from .basic_auth import basic_auth
from .token_auth import token_auth

multi_auth  = MultiAuth(token_auth, basic_auth)

@token_auth.get_user_roles
@basic_auth.get_user_roles
def get_user_roles(context):
  return context['role']
