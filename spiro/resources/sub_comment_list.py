from easydict import EasyDict
from copy import deepcopy
from flask_restful import Resource, marshal_with, fields as restful_fields
from webargs import fields as webargs_fields
from webargs.flaskparser import use_args

from .comment import full_comment_response_fields_without_error

from ..common.exceptions import *
from ..common.utils import MarshalJsonItem
from ..db import Comment

request_args = EasyDict()
request_args.get = {
  "article_id":               webargs_fields.Int(required=True),
  "parent_comment_id":        webargs_fields.Int(required=True),
  "sub_comment_offset":       webargs_fields.Int(required=True),
  "sub_comment_count":        webargs_fields.Int(required=True)
}

response_fields = EasyDict()
response_fields.get = {
  "article_id":   restful_fields.Integer(),
  "comment_list": restful_fields.List(restful_fields.Nested(full_comment_response_fields_without_error)),
  "error_code":   restful_fields.Integer(default = ErrorCode.EC_SUCCESS.value),
  "error_hint":   MarshalJsonItem(default = ""),
  "error_msg":    restful_fields.String(default = "")
}

class SubCommentListApi(Resource):
  @use_args(request_args.get, location="query")
  @marshal_with(response_fields.get)
  def get(self, args):
    article_id                  = args["article_id"]
    parent_comment_id            = args["parent_comment_id"]
    sub_comment_offset          = args["sub_comment_offset"]
    sub_comment_count           = args["sub_comment_count"]
    
    return get_sub_comment_list(
      article_id,
      parent_comment_id,
      sub_comment_offset,
      sub_comment_count
    )

@handle_exception
def get_sub_comment_list(article_id, parent_comment_id, sub_comment_offset, sub_comment_count):
  if sub_comment_offset < 0:
    raise ArgInvalid("primary comment offset is less than 0")

  if sub_comment_count < 0:
    raise ArgInvalid("primary comment count is less than 0")

  # TODO: restrict primary_comment_count and sub_comment_count below 128?

  if sub_comment_count < 0:
    raise ArgInvalid("sub comment count is less than 0")

  flag, sub_comments = Comment.find_rangeof_sub_comments_by_parent_comment_id(parent_comment_id, sub_comment_offset, sub_comment_count)
  
  if flag:
    return {
      "article_id": article_id,
      "comment_list": sub_comments
    }
  else:
    raise DbNotFound