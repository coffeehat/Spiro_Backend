from flask import request
from flask_httpauth import HTTPBasicAuth

from .user_logic import register_user, verify_user

from ..common.exceptions import *

basic_auth = HTTPBasicAuth()

@basic_auth.verify_password
def verify_pass(user_name_or_email, user_passwd):
  if user_name_or_email == "" and user_passwd == "":
    # If Client provides Authentication header, but with no username and no password
    # We consider it as a Visitor
    # and retrieve the username and email info from body
    form = request.form
    return _handle_visitor(form["user_name"], form["user_email"])
  elif user_name_or_email == "" or user_passwd == "":
    return _handle_arg_error()
  else:
    # If Client provides Authentication header without empty username and password
    # We consider it as a registered Member/Admin
    # Notice that this code branch shouldn't be executed because we have token authentication
    return _handle_registered(user_name_or_email, user_passwd)

@handle_exception_tlocal
def _handle_arg_error():
  raise ArgInvalid

@handle_exception_tlocal
def _handle_registered(username_or_email, user_passwd):
  return verify_user(username_or_email, user_passwd)

@handle_exception_tlocal
def _handle_visitor(user_name, user_email):
  # For visitors, we don't need to verify email
  return register_user(user_name, user_email)[0]