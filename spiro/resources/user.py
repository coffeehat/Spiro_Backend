from flask_restful import Resource, marshal_with, fields as restful_fields
from webargs import validate, fields as webargs_fields
from webargs.flaskparser import use_args

from ..common.exceptions import *
from ..auth.user_logic import register_user, verify_user
from ..common.utils import generate_token, MarshalJsonItem
from ..db.user import User

# TODO: How to override webargs's error response?
request_args = {
  "method":   webargs_fields.String(required=True),
  "password": webargs_fields.String(required=True, validate=validate.Length(min=1)),
  "username": webargs_fields.String(),
  "email":    webargs_fields.String(),
}

response_fields = {
  "error_code": restful_fields.Integer(default = ErrorCode.EC_SUCCESS.value),
  "error_hint": MarshalJsonItem(default = ""),
  "error_msg": restful_fields.String(default = ""),
  "token": restful_fields.String(default = "")
}

class UserApi(Resource):
  @use_args(request_args, location="json")
  @marshal_with(response_fields)
  def post(self, args):
    username = args['username']
    password = args['password']
    if args["method"] == "register":
      email = args['email']
      if not username or not password:
        raise ArgInvalid
      return _register_user(username, email, password)
    elif args["method"] == "login":
      if not username:
        raise ArgInvalid
      return _login_user(username, password)
    else:
      raise ArgInvalid

@handle_exception
def _register_user(username, email, password):
  register_user(username, email, password)
  return {}

@handle_exception
def _login_user(username, password):
  user = verify_user(username, password)
  token = generate_token(user.id, seconds=1000)
  return {
    "token": token
  }