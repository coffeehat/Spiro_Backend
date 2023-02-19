from flask import make_response
from flask_restful import Resource

from ..config import SpiroConfig
from ..common.exceptions import *
from ..common.register_verify import handle_verification

class EmailVerificationApi(Resource):
  def get(self, veri_id):
    ret = _handle_verification(veri_id)
    if ret is None:
      body = verify_result_html.format(
        title = f"{SpiroConfig.website_name} - 邮箱验证",
        status = "邮箱验证成功！")
    else:
      body = verify_result_html.format(
        title = f"{SpiroConfig.website_name} - 邮箱验证",
        status = "邮箱验证失败")
    return make_response(body, 200, {"Content-Type": "text/html"})

verify_result_html = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta http-equiv="X-UA-Compatible" content="IE=edge">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{title}</title>
</head>
<body>
  <h1>{status}</h1>
</body>
</html>
"""

@handle_exception
def _handle_verification(veri_id):
  return handle_verification(veri_id)
