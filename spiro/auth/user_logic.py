
from ..common.defs import Role
from ..common.exceptions import *

from ..common.utils import get_password_hash, get_time_stamp
from ..db import User

def register_user(username, email = None, password = None):
  """
  Logics for registering user
  * If only username is provided, we register a visitor without email
  * If username and email are provided, we register a vistor with email
  * If username/email/password are provided, we register a member
  """
  if not username:
    raise ArgNoUsername

  if not email and password:
    raise ArgNoEmailButHasPasswd

  if email:
    return _handle_registration_with_email(username, email, password)
  else:
    return _handle_registration_without_email(username)

def _handle_registration_with_email(username, email, password=None):
  flag, users = User.find_user_by_username_or_email(username, email)
  
  if flag \
      and len(users) == 1 \
      and users[0].name == username \
      and users[0].email == email:
    # We find the very user who has same username and email!
    if users[0].role < Role.Visitor.value:
      raise UserRegDupBothNameAndEmailException
    else:
      if password:
        # We need to update the password to this visitor, that is turn the visitor into a member
        return _update_visitor_to_registered(users[0].id, username, email, password)
      else:
        # We don't need password here, so we just return that user
        return {
          "id":       users[0].id,
          "username": users[0].name,
          "email":    users[0].email,
          "role":     users[0].role
        }

  if flag:
    # We find some users, but they either has different username or different email
    if len(users) > 2:
      pass # TODO: logging this abnormal case, the size of the users here should be no more than 2
    name_dup = None
    email_dup = None
    for user in users:
      if user.name == username:
        name_dup = user
        continue
      if user.email == email:
        email_dup = user
        continue
    
    if name_dup and email_dup:
      if name_dup.role < Role.Visitor.value and email_dup.role < Role.Visitor.value:
        raise UserRegDupBothNameAndEmailException
      elif name_dup.role < Role.Visitor.value and email_dup.role >= Role.Visitor.value:
        # TODO: suggest to change the name to the dup one
        # Duplicate User Name with a member, dup E-mail with visitor whose name is xxx
        raise UserRegDupBothNameAndEmailException(
            error_hint = {
              "dup.name": {
                "role": Role.Visitor.value,
                "name": email_dup.name,
              }},
            error_msg = f"Dup E-mail with a visitor whose name is {email_dup.name}"
          )
      elif name_dup.role >= Role.Visitor.value and email_dup.role < Role.Visitor.value:
        if name_dup.email == "":
          raise UserRegDupEmailException
        else:
          raise UserRegDupBothNameAndEmailException
      else:
        if name_dup.email == "":
          raise UserRegDupEmailException(
            error_hint = {
              "dup.name": {
                "role": Role.Visitor.value,
                "name": email_dup.name,
              }},
            error_msg = f"Dup E-mail with a visitor whose name is {email_dup.name}"
          )
        else:
          # TODO: suggest to change the name to the dup one or correct you email
          raise UserRegDupBothNameAndEmailException(
            error_hint = {
              "dup.name": {
                "role": Role.Visitor.value,
                "name": email_dup.name,
              }},
            error_msg = f"Duplicate User Name with a vistor, dup E-mail with a visitor whose name is {email_dup.name}"
          )

    if name_dup:
      if name_dup.role < Role.Visitor.value:
        raise UserRegDupNameException
      else:
        if name_dup.email == "":
          if password:
            return _update_visitor_to_registered(name_dup.id, username, email, password)
          else:
            return _update_visitor_email(name_dup.id, username, email)
        else:
          raise UserRegDupNameException

    if email_dup:
      if email_dup.role < Role.Visitor.value:
        raise UserRegDupEmailException
      else:
        # TODO: suggest to change the name to the dup one
        raise UserRegDupEmailException(
            error_hint = {
              "dup.name": {
                "role": Role.Visitor.value,
                "name": email_dup.name,
              }},
            error_msg = f"Dup E-mail with a visitor whose name is {email_dup.name}"
          )

    raise InternalError  # TODO: logging this abnormal case, the code path shouldn't be run here
  else:
    return _register_new_user(username, email, password)


def _handle_registration_without_email(username):
  flag, user = User.find_user_by_username(username)
  if flag \
      and user.email == "":
    if user.role < Role.Visitor.value:
      pass # TODO: logging this abornal case, user with Role greater than Visitor shouldn't have empty email
    return {
      "id":       user.id,
      "username": user.name,
      "email":    user.email,
      "role":     user.role
    }
  
  if flag \
      and user.email != "":
    if user.role < Role.Visitor.value:
      raise UserRegDupNameException (
        error_msg = f"{username} is taken by a member"
      )
    else:
      raise UserRegDupNameException (
        error_msg = f"{username} is taken by a visitor"
      )
  
  if not flag:
    return _register_new_user(username, "")

  return None # TODO: logging this abnormal case, the code path shouldn't be run here

def _update_visitor_to_registered(user_id, username, email, password):
  User.update_user(
    user_id,
    {
      "name": username,
      "email": email,
      "role": Role.Member.value,
      "password": get_password_hash(password),
      "register_timestamp": get_time_stamp()
    }
  )
  return {
    "id":       user_id,
    "username": username,
    "email":    email,
    "role":     Role.Member.value
  }

def _update_visitor_email(user_id, username, email):
  User.update_user(
    user_id,
    {
      "email": email
    }
  )
  return {
    "id":       user_id,
    "username": username,
    "email":    email,
    "role":     Role.Visitor.value
  }

def _register_new_user(username, email, password = None):
  role = Role.Member.value              if password else Role.Visitor.value
  hash = get_password_hash(password)    if password else ""
  register_timestamp = get_time_stamp() if password else 0

  user = User(
    name = username,
    email = email,
    role  = role,
    password = hash,
    register_timestamp = register_timestamp
  )
  id = User.add_user_and_return_id(user)

  return {
    "id":       id,
    "username": username,
    "email":    email,
    "role":     role
  }