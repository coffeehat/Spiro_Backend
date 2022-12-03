from easydict import EasyDict
from flask_restful import Resource, marshal_with, fields as restful_fields
from webargs import fields as webargs_fields
from webargs.flaskparser import use_args

from ..common.utils import is_email
from ..auth.user_manage import register_user, login_user


request_args = {
  "method":   webargs_fields.String(required=True),
  "username": webargs_fields.String(),
  "password": webargs_fields.String(),
  "email":    webargs_fields.String(validate=is_email),
}

response_fields = {
  "error_code": restful_fields.Integer(),
  "error_msg": restful_fields.String(),
  "status_code": restful_fields.Integer(),
  "status_msg": restful_fields.String(),
  "token": restful_fields.String()
}

class UserApi(Resource):
  @use_args(request_args, location="json")
  @marshal_with(response_fields)
  def post(self, args):
    username = args['username']
    password = args['password']
    if args["method"] == "register":
      email = args['email']
      return register_user(username, email, password)
    elif args["method"] == "login":
      return login_user(username, password)
