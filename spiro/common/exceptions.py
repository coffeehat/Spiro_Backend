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
      return {"error_code": ErrorCode.EC_GENERIC_ERROR.value}, 500
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
      g.error = {"error_code": ErrorCode.EC_GENERIC_ERROR.value}
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

  # Database Error
  EC_DB_GENERIC_ERROR = 200
  EC_DB_NOT_FOUND_ERROR = 201
  
  # User Error
  EC_USER_GENERIC_ERROR = 300

  EC_USER_REG_ERROR = 301
  EC_USER_REG_DUP_NAME_ERROR = 302
  EC_USER_REG_DUP_EMAIL_ERROR = 303
  EC_USER_REG_DUP_BOTH_NAME_EMAIL_ERROR = 304

  EC_USER_LOGIN_ERROR = 350
  EC_USER_LOGIN_TOKEN_EXPIRED = 351
  EC_USER_LOGIN_TOKEN_SIGN_ERROR = 352

  EC_USER_UNAUTHORIZED_ERROR = 399

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

# Exception for User

class UserException(CommonException):
  def __init__(self, error_hint = "", error_msg = ""):
    super(CommonException, self).__init__(
      error_hint = error_hint,
      error_msg  = error_msg,
      error_code = ErrorCode.EC_DB_NOT_FOUND_ERROR,
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

class UserUnAuthorizedException(CommonException):
  def __init__(self, error_hint = "", error_msg = ""):
    super(CommonException, self).__init__(
      error_hint = error_hint,
      error_msg  = error_msg,
      error_code = ErrorCode.EC_USER_UNAUTHORIZED_ERROR,
      http_status_code = 400
    )