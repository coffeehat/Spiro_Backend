from easydict import EasyDict
from flask_restful import Resource, marshal_with, fields as restful_fields
from webargs import fields as webargs_fields
from webargs.flaskparser import use_args

from ..db import get_comment, save_comment

request_args = EasyDict()
request_args.get = {
  "comment_id":   webargs_fields.Integer(required=True),
}
request_args.post = {
  "article_id":   webargs_fields.Integer(),
  "comment":      webargs_fields.String()
}

response_fields = EasyDict()
response_fields.get = {
  "article_id":   restful_fields.Integer(),
  "comment_id":   restful_fields.Integer(),
  "comment_time": restful_fields.DateTime(dt_format="rfc822"),
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
  @marshal_with(response_fields.post)
  def post(self, args):
    article_id = args["article_id"]
    comment = args["comment"]

    return save_comment(article_id, comment)
