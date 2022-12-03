import sqlalchemy as sa

from ..db import db
from ..common.utils import is_email

class User(db.Model):
  id            = sa.Column(sa.Integer, primary_key=True)
  username      = sa.Column(sa.String,  nullable=False, unique=True)
  email         = sa.Column(sa.String,  nullable=False, unique=True)
  role          = sa.Column(sa.String,  nullable=False)
  password      = sa.Column(sa.String)
  register_timestamp = sa.Column(sa.Integer)

  @staticmethod
  def find_user_by_username_or_email(uname_or_email):
    if is_email(uname_or_email):
      return User.find_user_by_email(uname_or_email)
    else:
      return User.find_user_by_username(uname_or_email)

  @staticmethod
  def find_user_by_username(username):
    user = db.session.execute(sa.select(User) \
      .where(User.username == username) \
      .limit(1)
    ).scalars().first()
    if user:
      return True, user
    else:
      return False, None

  @staticmethod
  def find_user_by_email(email):
    user = db.session.execute(sa.select(User) \
      .where(User.email == email) \
      .limit(1)
    ).scalars().first()
    if user:
      return True, user,
    else:
      return False, None

  @staticmethod
  def find_user_by_id(id):
    user = db.session.execute(sa.select(User) \
      .where(User.id == id) \
      .limit(1)
    ).scalars().first()
    if user:
      return True, user,
    else:
      return False, None

  # Tutorial for sqlalchemy
  # https://docs.sqlalchemy.org/en/14/core/tutorial.html#selecting

  @staticmethod
  def is_username_dup(username):
    ret = db.session.execute(
      sa.select(sa.func.count().label("count")) \
      .where(User.username == username) \
      .limit(1)
    ).first()
    return ret["count"] > 0

  @staticmethod
  def is_email_dup(email):
    ret = db.session.execute(
      sa.select(sa.func.count().label("count")) \
      .where(User.email == email) \
      .limit(1)
    ).first()
    return ret["count"] > 0
  
  @staticmethod
  def add_user(user):
    db.session.add(user)
    db.session.commit()
