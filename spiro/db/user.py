import sqlalchemy as sa
import typing

from ..db import db
from ..common.utils import is_email

class User(db.Model):
  user_id                 = sa.Column(sa.Integer, primary_key=True)
  user_name               = sa.Column(sa.String,  nullable=False, unique=True)
  user_email              = sa.Column(sa.String,  unique=True)
  user_role               = sa.Column(sa.Integer, nullable=False)
  user_passwd             = sa.Column(sa.String)
  user_register_timestamp = sa.Column(sa.Integer)

  @staticmethod
  def find_user_by_username_and_email(user_name, user_email) -> typing.Tuple[bool, typing.Optional['User']]:
    user = db.session.execute(sa.select(User) \
      .where(sa.and_(User.user_name == user_name, User.user_email == user_email)) \
      .limit(1)
    ).scalars().first()
    if user:
      return True, user
    else:
      return False, None

  @staticmethod
  def find_users_by_username_or_email(user_name, user_email) -> typing.Tuple[bool, typing.Optional[typing.List['User']]]:
    users = db.session.execute(sa.select(User) \
      .where(sa.or_(User.user_name == user_name, User.user_email == user_email)) \
    ).scalars().all()
    if len(users):
      return True, users
    else:
      return False, None

  @staticmethod
  def find_user_by_username_or_by_email(user_name_or_email) -> typing.Tuple[bool, typing.Optional['User']]:
    if is_email(user_name_or_email):
      return User.find_user_by_email(user_name_or_email)
    else:
      return User.find_user_by_username(user_name_or_email)

  @staticmethod
  def find_user_by_username(user_name) -> typing.Tuple[bool, typing.Optional['User']]:
    user = db.session.execute(sa.select(User) \
      .where(User.user_name == user_name) \
      .limit(1)
    ).scalars().first()
    if user:
      return True, user
    else:
      return False, None

  @staticmethod
  def find_user_by_email(user_email) -> typing.Tuple[bool, typing.Optional['User']]:
    user = db.session.execute(sa.select(User) \
      .where(User.user_email == user_email) \
      .limit(1)
    ).scalars().first()
    if user:
      return True, user,
    else:
      return False, None

  @staticmethod
  def find_user_by_id(user_id) -> typing.Tuple[bool, typing.Optional['User']]:
    user = db.session.execute(sa.select(User) \
      .where(User.user_id == user_id) \
      .limit(1)
    ).scalars().first()
    if user:
      return True, user,
    else:
      return False, None

  # Tutorial for sqlalchemy
  # https://docs.sqlalchemy.org/en/14/core/tutorial.html#selecting

  @staticmethod
  def is_username_dup(user_name) -> bool:
    ret = db.session.execute(
      sa.select(sa.func.count().label("count")) \
      .where(User.user_name == user_name) \
      .limit(1)
    ).first()
    return ret["count"] > 0

  @staticmethod
  def is_email_dup(user_email) -> bool:
    ret = db.session.execute(
      sa.select(sa.func.count().label("count")) \
      .where(User.user_email == user_email) \
      .limit(1)
    ).first()
    return ret["count"] > 0

  @staticmethod
  def add_user(user) -> None:
    db.session.add(user)
    db.session.commit()

  @staticmethod
  def add_user_and_return_id(user) -> int:
    ret = db.session.execute(
      sa.text(
        f"INSERT INTO {User.__table__.name} \
          (user_name, user_email, user_role, user_passwd, user_register_timestamp) \
          VALUES (:user_name, :user_email, :user_role, :user_passwd, :user_register_timestamp) \
          RETURNING user_id"
      ),
      {
        "user_name":               user.user_name, 
        "user_email":              user.user_email,
        "user_role":               user.user_role, 
        "user_passwd":             user.user_passwd,
        "user_register_timestamp": user.user_register_timestamp
      }
    ).first()
    user_id = ret[0]
    db.session.commit()
    return user_id

  @staticmethod
  def update_user(user_id, user):
    db.session.execute(
      sa.update(User) \
      .values(user) \
      .where(User.user_id == user_id) \
    )
    db.session.commit()