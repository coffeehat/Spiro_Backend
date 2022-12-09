from flask import g
from flask_httpauth import MultiAuth
from flask_restful import marshal

from .basic_auth import basic_auth
from .token_auth import token_auth

from ..common.exceptions import *
from ..resources.user import response_fields as user_response_fields

multi_auth  = MultiAuth(token_auth, basic_auth)

@token_auth.error_handler
@basic_auth.error_handler
def handle_error(status):
  if hasattr(g, "error") and hasattr(g, "status"):
    error, status =  g.error, g.status
  else:
    e = UserUnAuthorizedException()
    error, status = e.get_error_info(), e.get_http_status()

  return marshal(error, user_response_fields), status

@token_auth.get_user_roles
@basic_auth.get_user_roles
def get_user_roles(context):
  return context.role