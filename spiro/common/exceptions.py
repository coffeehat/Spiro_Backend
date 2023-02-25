import enum

from flask import g
from functools import wraps

def handle_exception(func):
  @wraps(func)
  def wrapper(*args, **kwargs):
    try:
      comment = func(*args, **kwargs)
    except CommonException as e:
      return e.get_error_info(), e.get_http_status()
    except Exception as e:
      return {"error_code": ErrorCode.EC_INTERNAL_ERROR.value}, 500
    return comment
  return wrapper

def handle_exception_tlocal(func):
  @wraps(func)
  def wrapper(*args, **kwargs):
    try:
      return func(*args, **kwargs)
    except CommonException as e:
      g.error = e.get_error_info()
      g.status = e.http_status_code
      return None
    except Exception as e:
      g.error = {"error_code": ErrorCode.EC_INTERNAL_ERROR.value}
      g.status = 500
      return None
  return wrapper

class ErrorCode(enum.Enum):
  # Generics
  EC_SUCCESS = 0
  EC_GENERIC_ERROR = 1
  EC_INTERNAL_ERROR = 2

  # Argument Error
  EC_ARG_GENERIC_ERROR = 100
  EC_ARG_INVALID_ERROR = 101
  EC_ARG_NOUSERNAME_ERROR = 102
  EC_ARG_NOEMAIL_BUT_HASPASSWD_ERROR = 103
  EC_ARG_EMPTY_COMMENT = 104
  EC_ARG_INVALID_ANCHOR = 105

  # Database Error
  EC_DB_GENERIC_ERROR = 200
  EC_DB_NOT_FOUND_ERROR = 201
  EC_DB_ANCHOR_NOT_FOUND_ERROR = 202
  
  # User Error
  EC_USER_GENERIC_ERROR = 300

  EC_USER_REG_ERROR = 301
  EC_USER_REG_DUP_NAME_ERROR = 302
  EC_USER_REG_DUP_EMAIL_ERROR = 303
  EC_USER_REG_DUP_BOTH_NAME_EMAIL_ERROR = 304

  EC_VISITOR_REG_DUP_BOTH_NAME_EMAIL_WITH_MEMBER_ERROR = 305
  EC_VISITOR_REG_DUP_NAME_WITH_MEMBER_DUP_EMAIL_WITH_VISITOR = 306
  EC_VISIOTR_REG_DUP_EMAIL_WITH_MEMBER = 307
  EC_VISITOR_REG_DUP_NAME_WITH_VISITOR_DUP_EMAIL_WITH_MEMBER = 308
  EC_VISIOTR_REG_DUP_EMAIL_WITH_VISITOR = 309
  EC_VISIOTR_REG_DUP_BOTH_NAME_EMAIL_WITH_VISITOR_ERROR = 310
  EC_VISITOR_REG_DUP_NAME_WITH_MEMBER = 311

  EC_USER_LOGIN_ERROR = 350
  EC_USER_LOGIN_TOKEN_EXPIRED = 351
  EC_USER_LOGIN_TOKEN_SIGN_ERROR = 352
  EC_USER_LOGIN_AS_VISITOR_ERROR = 353
  
  EC_VISITOR_LOGIN_ERROR = 370
  EC_VISITOR_LOGIN_NEED_EMAIL = 371
  EC_VISITOR_LOGIN_NAME_CONLICT_WITH_MEMBER = 372
  EC_VISITOR_LOGIN_UNMATCHED_EMIAL_WITH_NAME = 373
  EC_VISITOR_LOGIN_NEED_PASSWD_AUTHENTICATION = 374

  EC_USER_EMAIL_NOT_VERIFED = 398
  EC_USER_UNAUTHORIZED_ERROR = 399

  EC_COMMENT_ERROR = 400
  EC_COMMENT_DELETE_ERROR = 401

# TODO: refine the http status code

class ExceptionABC(Exception):
  def __init__(self, error_code, error_hint, error_msg, http_status_code=400):
    self.http_status_code = http_status_code
    self.error_code = error_code
    self.error_hint = error_hint
    self.error_msg  = error_msg

  def get_error_info(self):
    return {
      "error_code": self.error_code.value,
      "error_hint": self.error_hint,
      "error_msg":  self.error_msg
    }
  
  def get_http_status(self):
    return self.http_status_code

class CommonException(ExceptionABC):
  def __init__(self, error_hint = "", error_msg = ""):
    super().__init__(
      error_hint = error_hint,
      error_msg  = error_msg,
      error_code = ErrorCode.EC_GENERIC_ERROR,
      http_status_code = 500
    )

class InternalError(CommonException):
  def __init__(self, error_hint = "", error_msg = ""):
    super(CommonException, self).__init__(
      error_hint = error_hint,
      error_msg  = error_msg,
      error_code = ErrorCode.EC_INTERNAL_ERROR,
      http_status_code = 500
    )

# Exceptions for arugment

class ArgException(CommonException):
  def __init__(self, error_hint = "", error_msg = ""):
    super(CommonException, self).__init__(
      error_hint = error_hint,
      error_msg  = error_msg,
      error_code = ErrorCode.EC_ARG_GENERIC_ERROR,
      http_status_code = 400
    )

class ArgInvalid(ArgException):
  def __init__(self, error_hint = "", error_msg = ""):
    super(CommonException, self).__init__(
      error_hint = error_hint,
      error_msg  = error_msg,
      error_code = ErrorCode.EC_ARG_INVALID_ERROR,
      http_status_code = 403
    )

class ArgNoUsername(ArgException):
  def __init__(self, error_hint = "", error_msg = ""):
    super(CommonException, self).__init__(
      error_hint = error_hint,
      error_msg  = error_msg,
      error_code = ErrorCode.EC_ARG_NOUSERNAME_ERROR,
      http_status_code = 403
    )

class ArgNoEmailButHasPasswd(ArgException):
  def __init__(self, error_hint = "", error_msg = ""):
    super(CommonException, self).__init__(
      error_hint = error_hint,
      error_msg  = error_msg,
      error_code = ErrorCode.EC_ARG_NOEMAIL_BUT_HASPASSWD_ERROR,
      http_status_code = 403
    )

class ArgEmptyComment(ArgException):
  def __init__(self, error_hint = "", error_msg = ""):
    super(CommonException, self).__init__(
      error_hint = error_hint,
      error_msg  = error_msg,
      error_code = ErrorCode.EC_ARG_EMPTY_COMMENT,
      http_status_code = 403
    )

class ArgInvalidAnchor(ArgException):
  def __init__(self, error_hint = "", error_msg = ""):
    super(CommonException, self).__init__(
      error_hint = error_hint,
      error_msg  = error_msg,
      error_code = ErrorCode.EC_ARG_INVALID_ANCHOR,
      http_status_code = 403
    )

# Exceptions for Db

class DbException(CommonException):
  def __init__(self, error_hint = "", error_msg = ""):
    super(CommonException, self).__init__(
      error_hint = error_hint,
      error_msg  = error_msg,
      error_code = ErrorCode.EC_DB_GENERIC_ERROR,
      http_status_code = 400
    )

class DbNotFound(DbException):
  def __init__(self, error_hint = "", error_msg = ""):
    super(CommonException, self).__init__(
      error_hint = error_hint,
      error_msg  = error_msg,
      error_code = ErrorCode.EC_DB_NOT_FOUND_ERROR,
      http_status_code = 404
    )

class DbAnchorNotFound(DbException):
  def __init__(self, error_hint = "", error_msg = ""):
    super(CommonException, self).__init__(
      error_hint = error_hint,
      error_msg  = error_msg,
      error_code = ErrorCode.EC_DB_ANCHOR_NOT_FOUND_ERROR,
      http_status_code = 404
    )

# Exception for User

class UserException(CommonException):
  def __init__(self, error_hint = "", error_msg = ""):
    super(CommonException, self).__init__(
      error_hint = error_hint,
      error_msg  = error_msg,
      error_code = ErrorCode.EC_USER_GENERIC_ERROR,
      http_status_code = 400
    )

class UserRegisterException(CommonException):
  def __init__(self, error_hint = "", error_msg = ""):
    super(CommonException, self).__init__(
      error_hint = error_hint,
      error_msg  = error_msg,
      error_code = ErrorCode.EC_USER_REG_ERROR,
      http_status_code = 400
    )

class UserRegDupNameException(UserRegisterException):
  def __init__(self, error_hint = "", error_msg = ""):
    super(CommonException, self).__init__(
      error_hint = error_hint,
      error_msg  = error_msg,
      error_code = ErrorCode.EC_USER_REG_DUP_NAME_ERROR,
      http_status_code = 400
    )

class UserRegDupEmailException(UserRegisterException):
  def __init__(self, error_hint = "", error_msg = ""):
    super(CommonException, self).__init__(
      error_hint = error_hint,
      error_msg  = error_msg,
      error_code = ErrorCode.EC_USER_REG_DUP_EMAIL_ERROR,
      http_status_code = 401
    )

class UserRegDupBothNameAndEmailException(UserRegisterException):
  def __init__(self, error_hint = "", error_msg = ""):
    super(CommonException, self).__init__(
      error_hint = error_hint,
      error_msg  = error_msg,
      error_code = ErrorCode.EC_USER_REG_DUP_BOTH_NAME_EMAIL_ERROR,
      http_status_code = 400
    )

class VisitorRegDupBothNameEmailWithMemberException(UserRegisterException):
  def __init__(self, error_hint = "", error_msg = ""):
    super(CommonException, self).__init__(
      error_hint = error_hint,
      error_msg  = error_msg,
      error_code = ErrorCode.EC_VISITOR_REG_DUP_BOTH_NAME_EMAIL_WITH_MEMBER_ERROR,
      http_status_code = 400
    )

class VisitorRegDupNameWithMemberDupEmailWithVisitor(UserRegisterException):
  def __init__(self, error_hint = "", error_msg = ""):
    super(CommonException, self).__init__(
      error_hint = error_hint,
      error_msg  = error_msg,
      error_code = ErrorCode.EC_VISITOR_REG_DUP_NAME_WITH_MEMBER_DUP_EMAIL_WITH_VISITOR,
      http_status_code = 400
    )

class VisitorRegDupEmailWithMember(UserRegisterException):
  def __init__(self, error_hint = "", error_msg = ""):
    super(CommonException, self).__init__(
      error_hint = error_hint,
      error_msg  = error_msg,
      error_code = ErrorCode.EC_VISIOTR_REG_DUP_EMAIL_WITH_MEMBER,
      http_status_code = 400
    )

class VisitorRegDupNameWithVisitorDupEmailWithMember(UserRegisterException):
  def __init__(self, error_hint = "", error_msg = ""):
    super(CommonException, self).__init__(
      error_hint = error_hint,
      error_msg  = error_msg,
      error_code = ErrorCode.EC_VISITOR_REG_DUP_NAME_WITH_VISITOR_DUP_EMAIL_WITH_MEMBER,
      http_status_code = 400
    )

class VisitorRegDupEmailWithVisitor(UserRegisterException):
  def __init__(self, error_hint = "", error_msg = ""):
    super(CommonException, self).__init__(
      error_hint = error_hint,
      error_msg  = error_msg,
      error_code = ErrorCode.EC_VISIOTR_REG_DUP_EMAIL_WITH_VISITOR,
      http_status_code = 400
    )

class VisitorRegDupBothNameEmailWithVisitorException(UserRegisterException):
  def __init__(self, error_hint = "", error_msg = ""):
    super(CommonException, self).__init__(
      error_hint = error_hint,
      error_msg  = error_msg,
      error_code = ErrorCode.EC_VISIOTR_REG_DUP_BOTH_NAME_EMAIL_WITH_VISITOR_ERROR,
      http_status_code = 400
    )

class VisitorRegDupNameWithMemberException(UserRegisterException):
  def __init__(self, error_hint = "", error_msg = ""):
    super(CommonException, self).__init__(
      error_hint = error_hint,
      error_msg  = error_msg,
      error_code = ErrorCode.EC_VISITOR_REG_DUP_NAME_WITH_MEMBER,
      http_status_code = 400
    )

class UserLoginException(CommonException):
  def __init__(self, error_hint = "", error_msg = ""):
    super(CommonException, self).__init__(
      error_hint = error_hint,
      error_msg  = error_msg,
      error_code = ErrorCode.EC_USER_LOGIN_ERROR,
      http_status_code = 400
    )

class UserLoginTokenExpired(UserLoginException):
  def __init__(self, error_hint = "", error_msg = ""):
    super(CommonException, self).__init__(
      error_hint = error_hint,
      error_msg  = error_msg,
      error_code = ErrorCode.EC_USER_LOGIN_TOKEN_EXPIRED,
      http_status_code = 400
    )

class UserLoginTokenSignException(UserLoginException):
  def __init__(self, error_hint = "", error_msg = ""):
    super(CommonException, self).__init__(
      error_hint = error_hint,
      error_msg  = error_msg,
      error_code = ErrorCode.EC_USER_LOGIN_TOKEN_SIGN_ERROR,
      http_status_code = 400
    )

class UserLoginAsVisitorError(UserLoginException):
  def __init__(self, error_hint = "", error_msg = ""):
    super(CommonException, self).__init__(
      error_hint = error_hint,
      error_msg  = error_msg,
      error_code = ErrorCode.EC_USER_LOGIN_AS_VISITOR_ERROR,
      http_status_code = 400
    )

class VisitorLoginException(UserLoginException):
  def __init__(self, error_hint = "", error_msg = ""):
    super(CommonException, self).__init__(
      error_hint = error_hint,
      error_msg  = error_msg,
      error_code = ErrorCode.EC_VISITOR_LOGIN_ERROR,
      http_status_code = 400
    )

class VisitorLoginNeedEmail(UserLoginException):
  def __init__(self, error_hint = "", error_msg = ""):
    super(CommonException, self).__init__(
      error_hint = error_hint,
      error_msg  = error_msg,
      error_code = ErrorCode.EC_VISITOR_LOGIN_NEED_EMAIL,
      http_status_code = 400
    )

class VisitorLoginNameConflictWithMember(UserLoginException):
  def __init__(self, error_hint = "", error_msg = ""):
    super(CommonException, self).__init__(
      error_hint = error_hint,
      error_msg  = error_msg,
      error_code = ErrorCode.EC_VISITOR_LOGIN_NAME_CONLICT_WITH_MEMBER,
      http_status_code = 400
    )

class VisitorLoginUnmatchedEmailWithName(UserLoginException):
  def __init__(self, error_hint = "", error_msg = ""):
    super(CommonException, self).__init__(
      error_hint = error_hint,
      error_msg  = error_msg,
      error_code = ErrorCode.EC_VISITOR_LOGIN_UNMATCHED_EMIAL_WITH_NAME,
      http_status_code = 400
    )

class VisitorLoginNeedPasswordAuthentication(UserLoginException):
  def __init__(self, error_hint = "", error_msg = ""):
    super(CommonException, self).__init__(
      error_hint = error_hint,
      error_msg  = error_msg,
      error_code = ErrorCode.EC_VISITOR_LOGIN_NEED_PASSWD_AUTHENTICATION,
      http_status_code = 400
    )

class UserEmailNotVerifedError(UserLoginException):
  def __init__(self, error_hint = "", error_msg = ""):
    super(CommonException, self).__init__(
      error_hint = error_hint,
      error_msg  = error_msg,
      error_code = ErrorCode.EC_USER_EMAIL_NOT_VERIFED,
      http_status_code = 400
    )

class UserUnAuthorizedException(CommonException):
  def __init__(self, error_hint = "", error_msg = ""):
    super(CommonException, self).__init__(
      error_hint = error_hint,
      error_msg  = error_msg,
      error_code = ErrorCode.EC_USER_UNAUTHORIZED_ERROR,
      http_status_code = 400
    )

class CommentException(CommonException):
  def __init__(self, error_hint = "", error_msg = ""):
    super(CommonException, self).__init__(
      error_hint = error_hint,
      error_msg  = error_msg,
      error_code = ErrorCode.EC_COMMENT_ERROR,
      http_status_code = 400
    )

class CommentDeleteError(CommentException):
  def __init__(self, error_hint = "", error_msg = ""):
    super(CommonException, self).__init__(
      error_hint = error_hint,
      error_msg  = error_msg,
      error_code = ErrorCode.EC_COMMENT_DELETE_ERROR,
      http_status_code = 400
    )