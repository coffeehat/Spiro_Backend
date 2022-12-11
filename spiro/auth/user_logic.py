
from ..common.defs import Role
from ..common.exceptions import *

from ..common.utils import get_password_hash, get_utc_timestamp, verify_password
from ..db import User

"""
!!! This is a logic hell of user management !!!
"""

class UserInfo:
  def __init__(self, user_id, user_name, user_email, user_role):
    self.user_id = user_id
    self.user_name = user_name
    self.user_email = user_email
    self.user_role = user_role

def verify_user(user_name_or_email, user_passwd):
  flag, user = User.find_user_by_username_or_by_email(user_name_or_email)
  if flag and verify_password(user_passwd, user.user_passwd):
    return UserInfo(user.user_id, user.user_name, user.user_email, user.user_role)
  else:
    raise UserLoginException

def register_user(user_name, user_email = None, user_passwd = None):
  """
  Logics for registering user
  * If only username is provided, we register a visitor without email
  * If username and email are provided, we register a vistor with email
  * If username/email/password are provided, we register a member
  """
  if not user_name:
    raise ArgNoUsername

  if not user_email and user_passwd:
    raise ArgNoEmailButHasPasswd

  if user_email:
    return _handle_registration_with_email(user_name, user_email, user_passwd)
  else:
    return _handle_registration_without_email(user_name)

def _handle_registration_with_email(user_name, user_email, user_passwd=None):
  flag, users = User.find_users_by_username_or_email(user_name, user_email)
  
  if flag \
      and len(users) == 1 \
      and users[0].user_name == user_name \
      and users[0].user_email == user_email:
    # We find the very user who has same username and email!
    if users[0].user_role < Role.Visitor.value:
      if user_passwd:
        raise UserRegDupBothNameAndEmailException
      else:
        raise VisitorLoginNeedPasswordAuthentication
    else:
      if user_passwd:
        # We need to update the password to this visitor, that is turn the visitor into a member
        return _update_visitor_to_registered(users[0].user_id, user_name, user_email, user_passwd)
      else:
        # We don't need password here, so we just return that user
        return UserInfo(users[0].user_id, users[0].user_name, users[0].user_email, users[0].user_role)

  if flag:
    # We find some users, but they either has different username or different email
    if len(users) > 2:
      pass # TODO: logging this abnormal case, the size of the users here should be no more than 2
    name_dup = None
    email_dup = None
    for user in users:
      if user.user_name == user_name:
        name_dup = user
        continue
      if user.user_email == user_email:
        email_dup = user
        continue
    
    if name_dup and email_dup:
      if name_dup.user_role < Role.Visitor.value and email_dup.user_role < Role.Visitor.value:
        if user_passwd:
          raise UserRegDupBothNameAndEmailException
        else:
          raise VisitorRegDupBothNameEmailWithMemberException
      elif name_dup.user_role < Role.Visitor.value and email_dup.user_role >= Role.Visitor.value:
        # TODO: suggest to change the name to the dup one
        # Duplicate User Name with a member, dup E-mail with visitor whose name is xxx
        error_hint = {
          "dup.name": {
            "user_role": Role.Visitor.value,
            "user_name": email_dup.user_name,
          }}
        if user_passwd:
          raise UserRegDupBothNameAndEmailException(error_hint = error_hint)
        else:
          raise VisitorRegDupNameWithMemberDupEmailWithVisitor(error_hint = error_hint)
      elif name_dup.user_role >= Role.Visitor.value and email_dup.user_role < Role.Visitor.value:
        if not name_dup.user_email:
          if user_passwd:
            raise UserRegDupEmailException
          else:
            raise VisitorRegDupEmailWithMember
        else:
          if user_passwd:
            raise UserRegDupBothNameAndEmailException
          else:
            raise VisitorRegDupNameWithVisitorDupEmailWithMember
      else:
        if not name_dup.user_email:
          error_hint = {
            "dup.name": {
              "user_role": Role.Visitor.value,
              "user_name": email_dup.user_name,
          }}
          if user_passwd:
            raise UserRegDupEmailException(error_hint = error_hint)
          else:
            raise VisitorRegDupEmailWithVisitor(error_hint = error_hint)
        else:
          # TODO: suggest to change the name to the dup one or correct you email
          error_hint = {
            "dup.name": {
              "user_role": Role.Visitor.value,
              "user_name": email_dup.user_name,
          }}
          if user_passwd:
            raise UserRegDupBothNameAndEmailException(error_hint=error_hint)
          else:
            raise VisitorRegDupBothNameEmailWithVisitorException(error_hint=error_hint)

    if name_dup:
      if name_dup.user_role < Role.Visitor.value:
        if user_passwd:
          raise UserRegDupNameException
        else:
          raise VisitorRegDupNameWithMemberException
      else:
        if not name_dup.user_email:
          if user_passwd:
            return _update_visitor_to_registered(name_dup.user_id, user_name, user_email, user_passwd)
          else:
            return _update_visitor_email(name_dup.user_id, user_name, user_email)
        else:
          raise VisitorLoginUnmatchedEmailWithName

    if email_dup:
      if email_dup.user_role < Role.Visitor.value:
        if user_passwd:
          raise UserRegDupEmailException
        else:
          raise VisitorRegDupEmailWithMember
      else:
        # TODO: suggest to change the name to the dup one
        error_hint = {
          "dup.name": {
            "user_role": Role.Visitor.value,
            "user_name": email_dup.user_name,
        }}
        if user_passwd:
          raise UserRegDupEmailException(error_hint=error_hint)
        else:
          raise VisitorRegDupEmailWithVisitor(error_hint=error_hint)

    raise InternalError  # TODO: logging this abnormal case, the code path shouldn't be run here
  else:
    return _register_new_user(user_name, user_email, user_passwd)


def _handle_registration_without_email(user_name):
  flag, user = User.find_user_by_username(user_name)
  if flag \
      and not user.user_email:
    if user.user_role < Role.Visitor.value:
      pass # TODO: logging this abornal case, user with Role greater than Visitor shouldn't have empty email
    return UserInfo(user.user_id, user.user_name, None, user.user_role)
  
  if flag \
      and user.user_email:
    if user.user_role < Role.Visitor.value:
      raise VisitorLoginNameConflictWithMember (
        error_msg = f"{user_name} is taken by a member"
      )
    else:
      raise VisitorLoginNeedEmail (
        error_msg = f"{user_name} is taken by a visitor"
      )
  
  if not flag:
    return _register_new_user(user_name, "")

  return None # TODO: logging this abnormal case, the code path shouldn't be run here

def _update_visitor_to_registered(user_id, user_name, user_email, user_passwd):
  User.update_user(
    user_id,
    {
      "user_name": user_name,
      "user_email": user_email,
      "user_role": Role.Member.value,
      "user_passwd": get_password_hash(user_passwd),
      "user_register_timestamp": get_utc_timestamp()
    }
  )
  return UserInfo(user_id, user_name, user_email, Role.Member.value)

def _update_visitor_email(user_id, user_name, user_email):
  User.update_user(
    user_id,
    {
      "user_email": user_email
    }
  )
  return UserInfo(user_id, user_name, user_email, Role.Visitor.value)

def _register_new_user(user_name, user_email, user_passwd = None):
  user_role = Role.Member.value                 if user_passwd else Role.Visitor.value
  user_hash = get_password_hash(user_passwd)    if user_passwd else None
  user_register_timestamp = get_utc_timestamp()    if user_passwd else None
  user_email = user_email                       if user_email  else None

  user = User(
    user_name = user_name,
    user_email = user_email,
    user_role  = user_role,
    user_passwd = user_hash,
    user_register_timestamp = user_register_timestamp
  )
  user_id = User.add_user_and_return_id(user)

  return UserInfo(user_id, user_name, user_email, user_role)
