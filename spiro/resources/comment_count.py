from easydict import EasyDict
from flask_restful import Resource, marshal_with, fields as restful_fields
from webargs import fields as webargs_fields
from webargs.flaskparser import use_args

from .comment import response_fields as comment_response_fields

from ..common.exceptions import *
from ..common.utils import MarshalJsonItem
from ..common.lock import r_lock
from ..db import Comment

request_args = EasyDict()
request_args.get = {
  "article_id":   webargs_fields.Int(required=True),
}

response_fields = EasyDict()
response_fields.get = {
  "article_id":   restful_fields.Integer(default = 0),
  "count":        restful_fields.Integer(default = 0),
  "error_code":   restful_fields.Integer(default = ErrorCode.EC_SUCCESS.value),
  "error_hint":   MarshalJsonItem(default = ""),
  "error_msg":    restful_fields.String(default = "")
}

class CommentCountApi(Resource):
  @r_lock
  @use_args(request_args.get, location="query")
  @marshal_with(response_fields.get)
  def get(self, args):
    article_id  = args["article_id"]
    
    return get_comment_count(article_id)

@handle_exception
def get_comment_count(article_id):
  count = Comment.get_comments_count_by_article_id(article_id)
  return {
    "article_id": article_id,
    "count": count
  }