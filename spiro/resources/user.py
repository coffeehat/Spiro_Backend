from easydict import EasyDict
from flask_restful import Resource, marshal_with, fields as restful_fields
from webargs import fields as webargs_fields
from webargs.flaskparser import use_args

from ..auth.token_auth import generate_token
from ..common.exceptions import *
from ..common.defs import Role
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
  flag, users = User.find_user_by_username_or_email(username, email)
  
  if flag \
      and len(users) == 1 \
      and users[0].name == username \
      and users[0].email == email:
    # We find the very user who has same username and email!
    if users[0].role < Role.Visitor.value:
      raise UserRegDupNameException("Duplicate User Name and E-mail")
    else:
      return _update_visitor_to_registered(users[0].id, username, email, password)

  if flag:
    # We find some users, but they either has different username or different email
    if len(users) > 2:
      pass # TODO: logging this abnormal case, the size of the users here should be no more than 2
    name_dup = None
    email_dup = None
    for user in users:
      if user.name == username:
        name_dup = user
        continue
      if user.email == email:
        email_dup = user
        continue
    
    if name_dup and email_dup:
      if name_dup.role < Role.Visitor.value and email_dup.role < Role.Visitor.value:
        raise UserRegDupNameException("Duplicate User Name and E-mail")
      elif name_dup.role < Role.Visitor.value and email_dup.role >= Role.Visitor.value:
        # TODO: suggest to change the name to the dup one
        raise UserRegDupNameException("Duplicate User Name with a member, dup E-mail with visitor whose name is xxx")
      elif name_dup.role >= Role.Visitor.value and email_dup.role < Role.Visitor.value:
        if name_dup.email == "":
          raise UserRegDupNameException("Duplicate E-mail")
        else:
          raise UserRegDupNameException("Duplicate User Name and E-mail")
      else:
        if name_dup.email == "":
          raise UserRegDupNameException("Dup E-mail with visitor whose name is xxx")
        else:
          # TODO: suggest to change the name to the dup one or correct you email
          raise UserRegDupNameException("Duplicate User Name with a vistor, dup E-mail with visitor whose name is xxx")

    if name_dup:
      if name_dup.role < Role.Visitor.value:
        raise UserRegDupNameException("Duplicate User Name")
      else:
        if name_dup.email == "":
          return _update_visitor_to_registered(name_dup.id, username, email, password)
        else:
          raise UserRegDupNameException("Duplicate User Name")

    if email_dup:
      if email_dup.role < Role.Visitor.value:
        raise UserRegDupEmailException("Duplicate Email")
      else:
        # TODO: suggest to change the name to the dup one
        raise UserRegDupEmailException("Consider to change the name")

    return # TODO: logging this abnormal case, the code path shouldn't be run here
  else:
    return _register_new_user(username, email, password)

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

def _update_visitor_to_registered(user_id, username, email, password):
  User.update_user(
    user_id,
    {
      "name": username,
      "email": email,
      "role": Role.Member.value,
      "password": get_password_hash(password),
      "register_timestamp": get_time_stamp()
    }
  )
  return {
    "error_code": 0,
    "error_msg": "",
    "status_code": 0,
    "status_msg": "",
    "token": ""
  }

def _register_new_user(username, email, password):
  user = User(
    name = username,
    email = email,
    role  = Role.Member.value,
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