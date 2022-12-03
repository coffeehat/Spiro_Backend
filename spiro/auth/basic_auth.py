from flask import request
from flask_httpauth import HTTPBasicAuth

from ..common.utils import is_email
from ..db.user import User

basic_auth = HTTPBasicAuth()

@basic_auth.verify_password
def verify_pass(username_or_email, password):
  # Support for visitors
  if username_or_email == "" and password == "":
    form = request.form
    return {
      "id":       0,
      "username": form["username"] \
        if "username" in form                           else "Anonymous",
      "email":    form["email"]    \
        if "email" in form and is_email(form["email"]) in form  else ""
    }

  flag, user = User.verify_user(username_or_email, password)
  if flag:
    return {
      "id":       user.id, 
      "username": user.name,
      "email":    user.email
    }
  else:
    return None