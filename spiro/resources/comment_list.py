from easydict import EasyDict
from flask_restful import Resource, marshal_with, fields as restful_fields
from webargs import fields as webargs_fields
from webargs.flaskparser import use_args

from .comment import comment_response_fields_without_error

from ..common.exceptions import *
from ..common.utils import MarshalJsonItem
from ..db import Comment

request_args = EasyDict()
request_args.get = {
  "article_id":   webargs_fields.Int(required=True),
  "offset":       webargs_fields.Int(required=True),
  "length":       webargs_fields.Int(required=True)
}

response_fields = EasyDict()
response_fields.get = {
  "article_id":   restful_fields.Integer(),
  "comment_list": restful_fields.List(restful_fields.Nested(comment_response_fields_without_error)),
  "error_code":   restful_fields.Integer(default = ErrorCode.EC_SUCCESS.value),
  "error_hint":   MarshalJsonItem(default = ""),
  "error_msg":    restful_fields.String(default = "")
}

class CommentListApi(Resource):
  @use_args(request_args.get, location="query")
  @marshal_with(response_fields.get)
  def get(self, args):
    article_id  = args["article_id"]
    offset      = args["offset"]
    length      = args["length"]
    
    return get_comment_list(article_id, offset, length)

@handle_exception
def get_comment_list(article_id, offset, length):
  if offset < 0:
    raise ArgInvalid("offset is less than 0")

  if length < 0:
    raise ArgInvalid("length is less than 0")

  flag, comments = Comment.find_rangeof_comments_by_article_id(article_id, offset, length)
  if flag:
    return {
      "article_id": article_id,
      "comment_list": comments
    }
  else:
    raise DbNotFound