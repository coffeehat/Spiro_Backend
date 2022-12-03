from flask import request
from flask_httpauth import HTTPBasicAuth, HTTPTokenAuth, MultiAuth
from jose import jwt
from jose.exceptions import ExpiredSignatureError, JWTError

from .utils import verify_password, is_email

from ..db.db_debug import db_users

SECERT_KEY = 'test'

basic_auth = HTTPBasicAuth()
token_auth = HTTPTokenAuth('Bearer')
multi_auth  = MultiAuth(basic_auth, token_auth)

@basic_auth.verify_password
def user_verify(username_or_email, password):
  if username_or_email == "" and password == "":
    form = request.form
    return {
      "id":       0,
      "username": form["username"] \
        if "username" in form                           else "Anonymous",
      "email":    form["email"]    \
        if "email" and is_email(form["email"]) in form  else ""
    }

  item = "email" if is_email(username_or_email) else "username"

  for key in db_users:
    if username_or_email == db_users[key][item]:
      if verify_password(password, db_users[key]['password']):
        return {
          "id":       key, 
          "username": db_users[key]['username'],
          "email":    db_users[key]['email']
        }
      else:
        return None

@token_auth.verify_token
def token_verify(token):
  try:
    payload = jwt.decode(token, SECERT_KEY)
    id = payload["uid"]
    return {
      "id":         id,
      "username":   db_users[id]['username'],
      "email":      db_users[id]['email']
    }
  except ExpiredSignatureError as e:
    return None
  except JWTError as e:
    return None
  except:
    return None

@token_auth.get_user_roles
@basic_auth.get_user_roles
def get_user_roles(context):
  if context["id"] == 0:
    return "Visitor"
  else:
    return "Member"
