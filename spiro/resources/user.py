from easydict import EasyDict
from flask_restful import Resource, marshal_with, fields as restful_fields
from flask_httpauth import HTTPBasicAuth
from webargs import fields as webargs_fields
from webargs.flaskparser import use_args

from ..db import user_register, user_verify

request_args = {
  "username": webargs_fields.String(),
  "password": webargs_fields.String(),
  "email": webargs_fields.String()
}

response_fields = {
  "error_code": restful_fields.Integer(),
  "error_msg": restful_fields.String(),
  "status_code": restful_fields.Integer(),
  "status_msg": restful_fields.String()
}

class UserRegister(Resource):
  @use_args(request_args, location="json")
  @marshal_with(response_fields)
  def post(self, args):
    username = args['username']
    password = args['password']
    email = args['email']

    return user_register(username, email, password)

auth = HTTPBasicAuth()

@auth.verify_password
def verify_password(username, password):
  return user_verify(username, password)