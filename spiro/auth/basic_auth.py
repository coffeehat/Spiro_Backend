from flask import request
from flask_httpauth import HTTPBasicAuth

from ..common.defs import Role
from ..common.utils import is_email
from ..db.user import User

basic_auth = HTTPBasicAuth()

@basic_auth.verify_password
def verify_pass(username_or_email, password):
  if username_or_email == "" and password == "":
    # If Client provides Authentication header, but with no username and no password
    # We consider it as a Visitor
    # and retrieve the username and email info from body
    form = request.form
    return _handle_visitor(form["username"], form["email"])
  elif username_or_email == "" or password == "":
    return None
  else:
    # If Client provides Authentication header without empty username and password
    # We consider it as a registered Member/Admin
    # Notice that this code branch shouldn't be executed because we have token authentication
    return _handle_registered(username_or_email, password)

def _handle_registered(username_or_email, password):
  flag, user = User.verify_user(username_or_email, password)
  if flag:
    return {
      "id":       user.id, 
      "username": user.name,
      "email":    user.email,
      "role":     user.role
    }
  else:
    return None # TODO: return user login failed

def _handle_visitor(username, email):
  # Checks
  if not username:
    return None # TODO: how to give error info in these returns?

  if email:
    if is_email(email):
      return _handle_visitor_with_email(username, email)
    else:
      return None # TODO: Return email parse failed
  else:
    return _handle_visitor_without_email(username)  

def _handle_visitor_with_email(username, email):
  flag, users = User.find_user_by_username_or_email(username, email)

  if flag \
      and len(users) == 1 \
      and users[0].name == username \
      and users[0].email == email:
    # We find the very user who has same username and email
    if users[0].role < Role.Visitor.value:
      return None # TODO: We already have this member/admin, please login to send
    else:
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
        return None # TODO "Duplicate User Name and E-mail"
      elif name_dup.role < Role.Visitor.value and email_dup.role >= Role.Visitor.value:
        # TODO: suggest to change the name to the dup one
        return None # TODO "Duplicate User Name with a member, dup E-mail with visitor whose name is xxx"
      elif name_dup.role >= Role.Visitor.value and email_dup.role < Role.Visitor.value:
        if name_dup.email == "":
          return None # TODO "Duplicate E-mail"
        else:
          return None # TODO "Duplicate User Name and E-mail"
      else:
        if name_dup.email == "":
          return None # TODO "Dup E-mail with visitor whose name is xxx"
        else:
          # TODO: suggest to change the name to the dup one or correct you email
          return None # TODO "Duplicate User Name with a vistor, dup E-mail with visitor whose name is xxx"

    if name_dup:
      if name_dup.role < Role.Visitor.value:
        return None # TODO "Duplicate User Name"
      else:
        if name_dup.email == "":
          ret = _update_visitor_email(name_dup.id, email)
          ret["username"] = username
          return ret
        else:
          return None # TODO "Duplicate User Name"

    if email_dup:
      if email_dup.role < Role.Visitor.value:
        return None # TODO "Duplicate Email"
      else:
        # TODO: suggest to change the name to the dup one
        return None # TODO "Consider to change the name"

    return None # TODO: logging this abnormal case, the code path shouldn't be run here
  else:
    return _register_new_visitor_account(username, email)

def _handle_visitor_without_email(username):
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
      return None # TODO: Return "name is taken by member/admin"
    else:
      return None # TODO: Return "name is taken by a visitor (don't tell the email)"
  
  if not flag:
    return _register_new_visitor_account(username, "")

  return None # TODO: logging this abnormal case, the code path shouldn't be run here

def _register_new_visitor_account(username, email):
  user = User(
    name                = username,
    email               = email,
    role                = Role.Visitor.value,
    password            = "",
    register_timestamp  = 0
  )
  id = User.add_user_and_return_id(user)
  return {
    "id":       id,
    "username": username,
    "email":    email,
    "role":     Role.Visitor.value
  }

def _update_visitor_email(user_id, email):
  User.update_user(
    user_id,
    {
      "email": email
    }
  )
  return {
    "id":       user_id,
    "email":    email,
    "role":     Role.Visitor.value
  }