from .token_auth import generate_token

from ..common.exceptions import *
from ..common.utils import get_password_hash, verify_password, get_time_stamp
from ..db.user import User

@handle_exception
def register_user(username, email, password):
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

@handle_exception
def login_user(username, password):
  flag, user = verify_user(username, password)
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

def verify_user(uname_or_email, password):
  flag, user = User.find_user_by_username_or_email(uname_or_email)
  if flag and verify_password(password, user.password):
    return True, user
  else:
    return False, None