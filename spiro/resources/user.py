from easydict import EasyDict
from flask_restful import Resource, marshal_with, fields as restful_fields
from webargs import fields as webargs_fields
from webargs.flaskparser import use_args

from ..auth.token_auth import generate_token
from ..common.exceptions import *
from ..common.utils import get_password_hash, get_time_stamp, is_email
from ..db.user import User


request_args = {
  "method":   webargs_fields.String(required=True),
  "username": webargs_fields.String(),
  "password": webargs_fields.String(),
  "email":    webargs_fields.String(validate=is_email),
}

response_fields = {
  "error_code": restful_fields.Integer(),
  "error_msg": restful_fields.String(),
  "status_code": restful_fields.Integer(),
  "status_msg": restful_fields.String(),
  "token": restful_fields.String()
}

class UserApi(Resource):
  @use_args(request_args, location="json")
  @marshal_with(response_fields)
  def post(self, args):
    username = args['username']
    password = args['password']
    if args["method"] == "register":
      email = args['email']
      return register_user(username, email, password)
    elif args["method"] == "login":
      return login_user(username, password)

@handle_exception
def register_user(username, email, password):
  # Duplication test
  if User.is_username_dup(username):
    raise UserRegDupNameException("Duplicate User Name")
  if User.is_email_dup(email):
      raise UserRegDupEmailException("Duplicate Email")
  
  # Save info to db
  user = User(
    name = username,
    email = email,
    role  = "Member",
    password = get_password_hash(password),
    register_timestamp = get_time_stamp()
  )
  User.add_user(user)

  return {
    "error_code": 0,
    "error_msg": "",
    "status_code": 0,
    "status_msg": "",
    "token": ""
  }

@handle_exception
def login_user(username, password):
  flag, user = User.verify_user(username, password)
  if (flag):
    token = generate_token(user.id, seconds=1000)
    return {
      "error_code": 0,
      "error_msg": "",
      "status_code": 0,
      "status_msg": "",
      "token": token
    }
  else:
    return {
      "error_code": 0,
      "error_msg": "",
      "status_code": 0,
      "status_msg": "",
      "token": ""
    }
