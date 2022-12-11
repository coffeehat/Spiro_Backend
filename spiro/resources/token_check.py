from easydict import EasyDict
from flask_restful import Resource, marshal_with, fields as restful_fields
from webargs import fields as webargs_fields
from webargs.flaskparser import use_args

from ..common.exceptions import *
from ..common.utils import MarshalJsonItem, decode_token

request_args = EasyDict()
request_args = {
  "token":        webargs_fields.String(required=True),
}

response_fields = EasyDict()
response_fields = {
  "error_code":   restful_fields.Integer(default = ErrorCode.EC_SUCCESS.value),
  "error_hint":   MarshalJsonItem(default = ""),
  "error_msg":    restful_fields.String(default = "")
}

class TokenCheckApi(Resource):
  @use_args(request_args, location="form")
  @marshal_with(response_fields)
  def post(self, args):
    token = args["token"]
    return check_token(token)

@handle_exception
def check_token(token):
  payload = decode_token(token)
  return {}