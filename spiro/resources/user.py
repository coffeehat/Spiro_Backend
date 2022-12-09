from flask_restful import Resource, marshal_with, fields as restful_fields
from webargs import validate, fields as webargs_fields
from webargs.flaskparser import use_args

from ..common.exceptions import *
from ..auth.user_logic import register_user
from ..common.utils import is_email, generate_token, MarshalJsonItem
from ..db.user import User

request_args = {
  "method":   webargs_fields.String(required=True),
  "username": webargs_fields.String(required=True, validate=validate.Length(min=1)),
  "password": webargs_fields.String(required=True, validate=validate.Length(min=1)) ,
  "email":    webargs_fields.String(required=True, validate=is_email),
}

response_fields = {
  "error_code": restful_fields.Integer(default = ErrorCode.EC_SUCCESS.value),
  "error_hint": MarshalJsonItem(default = ""),
  "error_msg": restful_fields.String(default = ""),
  "token": restful_fields.String(default = "")
}

class UserApi(Resource):
  @use_args(request_args, location="json", error_headers={"abc":"1234"})
  @marshal_with(response_fields)
  def post(self, args):
    username = args['username']
    password = args['password']
    if args["method"] == "register":
      email = args['email']
      return _register_user(username, email, password)
    elif args["method"] == "login":
      return _login_user(username, password)
    else:
      raise ArgInvalid

@handle_exception
def _register_user(username, email, password):
  register_user(username, email, password)
  return {}

@handle_exception
def _login_user(username, password):
  flag, user = User.verify_user(username, password)
  if (flag):
    token = generate_token(user.id, seconds=1000)
    return {
      "token": token
    }
  else:
    return {}