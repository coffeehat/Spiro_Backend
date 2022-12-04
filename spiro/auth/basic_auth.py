from flask import request
from flask_httpauth import HTTPBasicAuth

from ..common.defs import Role
from ..common.utils import is_email
from ..db.user import User

basic_auth = HTTPBasicAuth()

@basic_auth.verify_password
def verify_pass(username_or_email, password):
  if username_or_email == "" and password == "":
    # If Client provides Authentication header, but with no username and no password
    # We consider it as a Visitor
    # and retrieve the username and email info from body
    form = request.form
    return _handle_visitor(form["username"], form["email"])
  elif username_or_email == "" or password == "":
    return None
  else:
    # If Client provides Authentication header without empty username and password
    # We consider it as a registered Member/Admin
    # Notice that this code branch shouldn't be executed because we have token authentication
    return _handle_registered(username_or_email, password)

def _handle_registered(username_or_email, password):
  flag, user = User.verify_user(username_or_email, password)
  if flag:
    return {
      "id":       user.id, 
      "username": user.name,
      "email":    user.email,
      "role":     user.role
    }
  else:
    return None

def _handle_visitor(username, email):
  # Checks
  if not username:
    return None # TODO: how to give error info in these returns?
  if email and not is_email(email):
    return None

  flag_is_dup_uname = User.is_username_dup(username)
  flag_is_dup_email = User.is_email_dup(email) if email else True

  if flag_is_dup_email and flag_is_dup_uname:
    # That is we have one account find in the database
    return _get_visitor_account(username, email)
  elif flag_is_dup_uname or flag_is_dup_uname:
    # That is we have conflict to account in the database
    return None
  else:
    # Need to register new visitor account
    return _register_new_visitor_account(username, email)
    
def _get_visitor_account(username, email):
  flag, user = User.find_user_by_joint_username_and_email(username, email)
  if (flag and user.role == Role.Visitor):
    return {
      "id":       user.id,
      "username": user.name,
      "email":    user.email,
      "role":     user.role
    }
  else:
    return None

def _register_new_visitor_account(username, email):
  user = User(
    name                = username,
    email               = email,
    role                = Role.Visitor,
    password            = "",
    register_timestamp  = 0
  )
  id = User.add_user_and_return_id(user)
  return {
    "id":       id,
    "username": username,
    "email":    email,
    "role":     Role.Visitor
  }