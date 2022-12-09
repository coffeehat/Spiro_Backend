from flask_httpauth import HTTPTokenAuth

from .user_logic import UserInfo

from ..db.user import User
from ..common.exceptions import *
from ..common.utils import decode_token

SECERT_KEY = 'test'

token_auth = HTTPTokenAuth('Bearer')

@token_auth.verify_token
@handle_exception_tlocal
def verify_token(token):
  payload = decode_token(token)
  user_id = payload["uid"]
  flag, user = User.find_user_by_id(user_id)
  if not flag:
    raise DbNotFound
  return UserInfo(user_id, user.user_name, user.user_email, user.user_role)