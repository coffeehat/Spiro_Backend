from easydict import EasyDict
from flask_restful import Resource, marshal_with, fields as restful_fields
from webargs import fields as webargs_fields

from ..common.exceptions import *
from ..common.register_verify import handle_verification
from ..common.utils import MarshalJsonItem

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

class EmailVerificationApi(Resource):
  @marshal_with(response_fields)
  def get(self, veri_id):
    return _handle_verification(veri_id)

@handle_exception
def _handle_verification(veri_id):
  return handle_verification(veri_id)
