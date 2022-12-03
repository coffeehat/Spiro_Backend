from flask_httpauth import HTTPTokenAuth
from jose import jwt
from jose.exceptions import ExpiredSignatureError, JWTError

from ..common.exceptions import *
from ..common.utils import get_expire_time
from ..db.user import User

SECERT_KEY = 'test'

token_auth = HTTPTokenAuth('Bearer')

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