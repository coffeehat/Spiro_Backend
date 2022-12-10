from flask_restful import Resource, marshal_with, fields as restful_fields
from webargs import validate, fields as webargs_fields
from webargs.flaskparser import use_args

from ..common.exceptions import *
from ..auth.user_logic import register_user, verify_user
from ..common.utils import generate_token, MarshalJsonItem
from ..db.user import User

# TODO: How to override webargs's error response?
request_args = {
  "method":         webargs_fields.String(required=True),
  "user_passwd":    webargs_fields.String(required=True, validate=validate.Length(min=1)),
  "user_name":      webargs_fields.String(),
  "user_email":     webargs_fields.String(),
}

response_fields = {
  "error_code": restful_fields.Integer(default = ErrorCode.EC_SUCCESS.value),
  "error_hint": MarshalJsonItem(default = ""),
  "error_msg":  restful_fields.String(default = ""),
  "token":      restful_fields.String(default = ""),
  "token_expire": restful_fields.Integer(default = 0),
  "user_name":  restful_fields.String(default = "")
}

class UserApi(Resource):
  @use_args(request_args, location="form")
  @marshal_with(response_fields)
  def post(self, args):
    user_name = args['user_name']
    user_passwd = args['user_passwd']
    if args["method"] == "register":
      user_email = args['user_email']
      if not user_name or not user_passwd:
        raise ArgInvalid
      return _register_user(user_name, user_email, user_passwd)
    elif args["method"] == "login":
      if not user_name:
        raise ArgInvalid
      return _login_user(user_name, user_passwd)
    else:
      raise ArgInvalid

@handle_exception
def _register_user(user_name, user_email, user_passwd):
  register_user(user_name, user_email, user_passwd)
  return {}

@handle_exception
def _login_user(user_name, user_passwd):
  user = verify_user(user_name, user_passwd)
  token = generate_token(user.user_id, seconds=10)
  return {
    "token": token,
    "token_expire": 10,
    "user_name": user.user_name
  }