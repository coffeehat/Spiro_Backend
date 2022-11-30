from functools import wraps

def handle_exception(func):
  @wraps(func)
  def wrapper(*args, **kwargs):
    try:
      comment = func(*args, **kwargs)
    except DbNotFound as e:
      return {"error_msg": str(e)}, 404
    except DbException as e:
      return {"error_msg": str(e)}, 400
    except ArgInvalid as e:
      return {"error_msg": str(e)}, 403
    except ArgException as e:
      return {"error_msg": str(e)}, 400
    except CommonException as e:
      return {"error_msg": str(e)}, 500
    except Exception as e:
      return {"error_msg": "General Error"}, 500
    return comment, 200
  return wrapper
  
class CommonException(Exception):
  pass

# Exceptions for arugment

class ArgException(CommonException):
  pass

class ArgInvalid(ArgException):
  pass

# Exceptions for Db

class DbException(CommonException):
  pass

class DbNotFound(DbException):
  pass

# Exception for User

class UserException(CommonException):
  pass

class UserRegisterException(CommonException):
  pass

class UserRegDupNameException(UserRegisterException):
  pass

class UserRegDupEmailException(UserRegisterException):
  pass

class UserLoginException(CommonException):
  pass