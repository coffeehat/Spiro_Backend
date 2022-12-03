import sqlalchemy as sa

from ..db import db

from ..auth.token import generate_token
from ..common.exceptions import *
from ..common.utils import hash_password, verify_password, get_time_stamp, is_email

class User(db.Model):
  id            = sa.Column(sa.Integer, primary_key=True)
  username      = sa.Column(sa.String,  nullable=False, unique=True)
  email         = sa.Column(sa.String,  nullable=False, unique=True)
  role          = sa.Column(sa.String,  nullable=False)
  password      = sa.Column(sa.String)
  register_timestamp = sa.Column(sa.Integer)

@handle_exception
def user_register(username, email, password):
  # Duplication test
  if is_username_dup(username):
    raise UserRegDupNameException("Duplicate User Name")
  if is_email_dup(email):
      raise UserRegDupEmailException("Duplicate Email")
  
  # Save info to db
  user = User(
    username = username,
    email = email,
    role  = "Member",
    password = hash_password(password),
    register_timestamp = get_time_stamp()
  )
  db.session.add(user)
  db.session.commit()

  return {
    "error_code": 0,
    "error_msg": "",
    "status_code": 0,
    "status_msg": "",
    "token": ""
  }

@handle_exception
def user_login(username, password):
  flag, user = user_verify(username, password)
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

def user_verify(uname_or_email, password):
  if is_email(uname_or_email):
    email = uname_or_email
    user = db.session.execute(sa.select(User) \
      .where(User.email == email) \
      .limit(1)
    ).scalars().first()
  else:
    username = uname_or_email
    user = db.session.execute(sa.select(User) \
      .where(User.username == username) \
      .limit(1)
    ).scalars().first()
  if user and verify_password(password, user.password):
      return True, user
  else:
    return False, None

# Tutorial for sqlalchemy
# https://docs.sqlalchemy.org/en/14/core/tutorial.html#selecting

def is_username_dup(username):
  ret = db.session.execute(
    sa.select(sa.func.count().label("count")) \
    .where(User.username == username) \
    .limit(1)
  ).first()
  return ret["count"] > 0

def is_email_dup(email):
  ret = db.session.execute(
    sa.select(sa.func.count().label("count")) \
    .where(User.email == email) \
    .limit(1)
  ).first()
  return ret["count"] > 0