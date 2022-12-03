from easydict import EasyDict
from flask_restful import Resource, marshal_with, fields as restful_fields
from webargs import fields as webargs_fields
from webargs.flaskparser import use_args

from ..auth import multi_auth
from ..db import get_comment, save_comment

request_args = EasyDict()
request_args.get = {
  "comment_id":   webargs_fields.Integer(required=True),
}
request_args.post = {
  "article_id":   webargs_fields.Integer(required=True),
  "comment":      webargs_fields.String(required=True),
  "username":     webargs_fields.String(),
  "email":        webargs_fields.String()
}

response_fields = EasyDict()
response_fields.get = {
  "article_id":   restful_fields.Integer(),
  "username":     restful_fields.String(),
  "comment_id":   restful_fields.Integer(),
  "comment_time": restful_fields.String(),
  "comment":      restful_fields.String(),
  "error_msg":    restful_fields.String()
}
response_fields.post = response_fields.get

class Comment(Resource):
  @use_args(request_args.get, location="form")
  @marshal_with(response_fields.get)
  def get(self, args):
    comment_id = args["comment_id"]
    return get_comment(comment_id)

  @use_args(request_args.post, location="form")
  @multi_auth.login_required(role=["Visitor", "Member"])
  @marshal_with(response_fields.post)
  def post(self, args):
    article_id  = args["article_id"]
    comment     = args["comment"]
    username    = multi_auth.current_user()["username"]
    email       = multi_auth.current_user()["email"]

    return save_comment(article_id, username, comment)