import datetime
import re

from datetime import timezone
from flask_restful import fields as restful_fields
from jose import jwt
from jose.exceptions import ExpiredSignatureError, JWTError
from werkzeug.security import generate_password_hash, check_password_hash

from .exceptions import UserLoginTokenExpired, UserLoginTokenSignException
from ..config import SpiroConfig

def singleton(cls):
  instances = {}

  def inner():
    if cls not in instances:
      instances[cls] = cls()
      return instances[cls]
    return inner

# TODO: Use a more robust email verify pattern
email_pattern = re.compile(r'([A-Za-z0-9]+[.-_])*[A-Za-z0-9]+@[A-Za-z0-9-]+(\.[A-Z|a-z]{2,})+')

def is_email(s):
  return re.match(email_pattern, s)

def get_password_hash(password):
  return generate_password_hash(password + SpiroConfig.misc.pass_salt)

def verify_password(password, hash):
  return check_password_hash(hash, password + SpiroConfig.misc.pass_salt)

def get_current_time():
  return datetime.datetime.utcnow()

def get_utc_timestamp():
  dt = get_current_time()
  return convert_time_2_utc_timestamp(dt)

def convert_time_2_utc_timestamp(dt):
  utc_time = dt.replace(tzinfo=timezone.utc)
  return utc_time.timestamp()

def get_expire_time(expire_seconds):
  return get_current_time() + datetime.timedelta(seconds=expire_seconds)

def convert_expire_time_to_cookies_expire_string(dt):
  utc_time = dt.replace(tzinfo=timezone.utc)
  return utc_time.strftime("%a, %d %b %Y %H:%M:%S GMT")

class MarshalJsonItem(restful_fields.Raw):
  def format(self, value):
    return value

SECERT_KEY = 'test'

def generate_token(uid, seconds=20):
  expire = get_expire_time(seconds)

  token = {
    "exp": expire,
    "uid": uid,
    "sub": SECERT_KEY
  }
  return jwt.encode(claims=token, key=SECERT_KEY), convert_time_2_utc_timestamp(expire)

def decode_token(token):
  try:
    return jwt.decode(token, SECERT_KEY)
  except ExpiredSignatureError as e:
    raise UserLoginTokenExpired
  except JWTError as e:
    raise UserLoginTokenSignException
  except:
    raise