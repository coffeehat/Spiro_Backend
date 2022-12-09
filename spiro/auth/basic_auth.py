from flask import request
from flask_httpauth import HTTPBasicAuth

from .user_logic import register_user, verify_user

from ..common.exceptions import *
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

@handle_exception_tlocal
def _handle_registered(username_or_email, password):
  return verify_user(username_or_email, password)

@handle_exception_tlocal
def _handle_visitor(username, email):
  return register_user(username, email)