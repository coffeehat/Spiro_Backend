from flask import request
from flask_httpauth import HTTPBasicAuth, HTTPTokenAuth, MultiAuth

from .token_helpers import token_verify, generate_token

from ..common.exceptions import *
from ..common.utils import hash_password, verify_password, get_time_stamp, is_email
from ..db.user import User

basic_auth = HTTPBasicAuth()
token_auth = HTTPTokenAuth('Bearer')
multi_auth  = MultiAuth(basic_auth, token_auth)

@basic_auth.verify_password
def verify_pass(username_or_email, password):
  if username_or_email == "" and password == "":
    form = request.form
    return {
      "id":       0,
      "username": form["username"] \
        if "username" in form                           else "Anonymous",
      "email":    form["email"]    \
        if "email" and is_email(form["email"]) in form  else ""
    }

  flag, user = user_verify(username_or_email, password)
  if flag:
    return {
      "id":       user.id, 
      "username": user.username,
      "email":    user.email
    }
  else:
    return None

token_auth.verify_token_callback = token_verify

@token_auth.get_user_roles
@basic_auth.get_user_roles
def get_user_roles(context):
  if context["id"] == 0:
    return "Visitor"
  else:
    return "Member"

@handle_exception
def user_register(username, email, password):
  # Duplication test
  if User.is_username_dup(username):
    raise UserRegDupNameException("Duplicate User Name")
  if User.is_email_dup(email):
      raise UserRegDupEmailException("Duplicate Email")
  
  # Save info to db
  user = User(
    username = username,
    email = email,
    role  = "Member",
    password = hash_password(password),
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
def user_login(username, password):
  flag, user = user_verify(username, password)
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

def user_verify(uname_or_email, password):
  flag, user = User.find_user_by_username_or_email(uname_or_email)
  if flag and verify_password(password, user.password):
    return True, user
  else:
    return False, None
