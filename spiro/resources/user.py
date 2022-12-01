from easydict import EasyDict
from flask_restful import Resource, marshal_with, fields as restful_fields
from flask_httpauth import HTTPBasicAuth
from webargs import fields as webargs_fields
from webargs.flaskparser import use_args

from ..db import user_register, user_verify, user_login, verify_token

request_args = {
  "method":   webargs_fields.String(required=True),
  "username": webargs_fields.String(),
  "password": webargs_fields.String(),
  "email":    webargs_fields.String(),
}

response_fields = {
  "error_code": restful_fields.Integer(),
  "error_msg": restful_fields.String(),
  "status_code": restful_fields.Integer(),
  "status_msg": restful_fields.String(),
  "token": restful_fields.String()
}

class User(Resource):
  @use_args(request_args, location="json")
  @marshal_with(response_fields)
  def post(self, args):
    username = args['username']
    password = args['password']
    if args["method"] == "register":
      email = args['email']
      return user_register(username, email, password)
    elif args["method"] == "login":
      return user_login(username, password)

auth = HTTPBasicAuth()

@auth.verify_password
def verify_crediential(username, password):
  if len(password):
    return user_verify(username, password)[0]
  else:
    return verify_token(username)