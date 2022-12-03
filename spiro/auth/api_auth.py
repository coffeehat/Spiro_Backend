from flask import request
from flask_httpauth import HTTPBasicAuth, HTTPTokenAuth, MultiAuth
from jose import jwt
from jose.exceptions import ExpiredSignatureError, JWTError

from .user_manage import verify_user

from ..common.exceptions import *
from ..common.utils import get_expire_time, is_email
from ..db.user import User

SECERT_KEY = 'test'

basic_auth = HTTPBasicAuth()
token_auth = HTTPTokenAuth('Bearer')
multi_auth  = MultiAuth(basic_auth, token_auth)

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
        if "email" and is_email(form["email"]) in form  else ""
    }

  flag, user = verify_user(username_or_email, password)
  if flag:
    return {
      "id":       user.id, 
      "username": user.username,
      "email":    user.email
    }
  else:
    return None

@token_auth.verify_token
def verify_token(token):
  try:
    payload = jwt.decode(token, SECERT_KEY)
    id = payload["uid"]
    flag, user = User.find_user_by_id(id)
    if not flag:
      return None
    return {
      "id":         id,
      "username":   user.username,
      "email":      user.email
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

def generate_token(uid, seconds=20):
  expire = get_expire_time(seconds)

  token = {
    "exp": expire,
    "uid": uid,
    "sub": SECERT_KEY
  }
  return jwt.encode(claims=token, key=SECERT_KEY)