import re
import uuid

from ..common.exceptions import *
from ..common.time import get_time_stamp

db_comment = {}

@handle_exception
def get_comment_list(article_id, range_start = 0, range_end = -1):
  if range_start < 0:
    raise ArgInvalid("Range_start is less than 0")
  
  if range_end != -1 and range_end <= range_start:
    raise ArgInvalid("Range_end should be greater than Range_end, at least one")
  
  if article_id in db_comment:
    if range_end == -1 or range_end > len(db_comment[article_id]):
      return {
        "article_id": article_id,
        "comment_list": db_comment[article_id][range_start:]
      }
    elif range_end > 0 and range_end <= len(db_comment[article_id]):
      return {
        "article_id": article_id,
        "comment_list": db_comment[article_id][range_start:range_end]
      }
    else:
      raise ArgInvalid("Range_end invalid")
  else:
    raise DbNotFound("Article_id does not exist in backend")

@handle_exception
def get_comment(comment_id):
  for article_id in db_comment:
    for item in db_comment[article_id]:
      if item["comment_id"] == comment_id:
        return item
  raise DbNotFound("Comment_id does not exist in backend")

@handle_exception
def save_comment(article_id, user_id, comment):
  if not article_id in db_comment:
    db_comment[article_id] = []

  item = {
    "article_id":   article_id,
    "user_id":      user_id,
    "comment_id":   int(uuid.uuid4().hex, 16),
    "comment_time": str(get_time_stamp()),
    "comment":      comment
  }

  db_comment[article_id].append(item)
  return item

# For user

db_users = {}

import hashlib

def hash_password(password):
  if not isinstance(password, bytes):
    password = bytes(password, 'utf-8')
  m = hashlib.sha256()
  m.update(password)
  return m.hexdigest()

def verify_password(password, hash):
  if not isinstance(password, bytes):
    password = bytes(password, 'utf-8')
  m = hashlib.sha256()
  m.update(password)
  return m.hexdigest() == hash

@handle_exception
def user_register(username, email, password):
  # TODO: Need refinement in future
  # Duplication test
  for key in db_users:
    if username == db_users[key]['username']:
      raise UserRegDupNameException("Duplicate User Name")
    if email == db_users[key]['email']:
      raise UserRegDupEmailException("Duplicate Email")
  
  # Save Password
  hash = hash_password(password)
  user_id = int(uuid.uuid4().hex, 16)
  db_users[user_id] = {
    'username': username,
    'email': email,
    'password': hash
  }

  return {
    "error_code": 0,
    "error_msg": "",
    "status_code": 0,
    "status_msg": "",
    "token": ""
  }

@handle_exception
def user_login(username, password):
  flag, uid = user_verify(username, password)
  if (flag):
    token = generate_token(uid, seconds=1000)
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

email_pattern = re.compile(r'([A-Za-z0-9]+[.-_])*[A-Za-z0-9]+@[A-Za-z0-9-]+(\.[A-Z|a-z]{2,})+')

def user_verify(username, password):
  if re.match(email_pattern, username):
    email = username
    for key in db_users:
      if email == db_users[key]['email']:
        if verify_password(password, db_users[key]['password']):
          return True, key
        else:
          return False, None
  else:
    for key in db_users:
      if username == db_users[key]['username']:
        if verify_password(password, db_users[key]['password']):
          return True, key
        else:
          return False, None
    return False, None


from jose import jwt
from jose.exceptions import ExpiredSignatureError, JWTError
from datetime import datetime,timedelta

SECERT_KEY = 'test'

def generate_token(uid, seconds=20):
  expire = datetime.utcnow() + timedelta(seconds=seconds)

  token = {
    "exp": expire,
    "uid": uid,
    "sub": SECERT_KEY
  }
  return jwt.encode(claims=token, key=SECERT_KEY)

def verify_token(token):
  try:
    payload = jwt.decode(token, SECERT_KEY)
    return True, payload["uid"]
  except ExpiredSignatureError as e:
    return False, None
  except JWTError as e:
    return False, None