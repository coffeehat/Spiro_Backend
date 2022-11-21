from easydict import EasyDict
from flask_restful import Resource, marshal_with, fields as restful_fields
from webargs import fields as webargs_fields
from webargs.flaskparser import use_args

from .comment import response_fields as comment_response_fields
from ..db import get_comment_list

request_args = EasyDict()
request_args.get = {
  "article_id":   webargs_fields.Int(required=True),
  "range_start":  webargs_fields.Int(required=True),
  "range_end":    webargs_fields.Int(required=True)
}

response_fields = EasyDict()
response_fields.get = {
  "article_id":   restful_fields.Integer(),
  "comment_list": restful_fields.List(restful_fields.Nested(comment_response_fields.get)),
  "error_msg":    restful_fields.String()
}

class CommentList(Resource):
  @use_args(request_args.get, location="form")
  @marshal_with(response_fields.get)
  def get(self, args):
    article_id  = args["article_id"]
    range_start = args["range_start"] if not args["range_start"] is None else 0
    range_end   = args["range_end"]   if not args["range_end"]   is None else 0
    
    return get_comment_list(article_id, range_start, range_end)