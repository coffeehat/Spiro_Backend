import re

from werkzeug.security import generate_password_hash, check_password_hash

def hash_password(password):
  return generate_password_hash(password)

def verify_password(password, hash):
  return check_password_hash(hash, password)

# TODO: Use a more robust email verify pattern
email_pattern = re.compile(r'([A-Za-z0-9]+[.-_])*[A-Za-z0-9]+@[A-Za-z0-9-]+(\.[A-Z|a-z]{2,})+')

def is_email(s):
    return re.match(email_pattern, s)