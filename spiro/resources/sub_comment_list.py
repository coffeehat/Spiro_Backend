from easydict import EasyDict
from copy import deepcopy
from flask_restful import Resource, marshal_with, fields as restful_fields
from webargs import fields as webargs_fields
from webargs.flaskparser import use_args

from .comment import full_comment_response_fields_without_error

from ..common.exceptions import *
from ..common.lock import r_lock
from ..common.utils import MarshalJsonItem
from ..db import Comment

request_args = EasyDict()
request_args.get = {
  "article_uuid":             webargs_fields.String(required=True),
  "parent_comment_id":        webargs_fields.Int(required=True),
  "sub_comment_offset":       webargs_fields.Int(required=True),
  "sub_comment_count":        webargs_fields.Int(required=True)
}

response_fields = EasyDict()
response_fields.get = {
  "article_uuid":   restful_fields.String(),
  "sub_comment_list": restful_fields.List(restful_fields.Nested(full_comment_response_fields_without_error)),
  "is_more":      restful_fields.Boolean(),
  "error_code":   restful_fields.Integer(default = ErrorCode.EC_SUCCESS.value),
  "error_hint":   MarshalJsonItem(default = ""),
  "error_msg":    restful_fields.String(default = "")
}

class SubCommentListApi(Resource):
  @r_lock
  @use_args(request_args.get, location="query")
  @marshal_with(response_fields.get)
  def get(self, args):
    article_uuid                  = args["article_uuid"]
    parent_comment_id            = args["parent_comment_id"]
    sub_comment_offset          = args["sub_comment_offset"]
    sub_comment_count           = args["sub_comment_count"]
    
    return get_sub_comment_list(
      article_uuid,
      parent_comment_id,
      sub_comment_offset,
      sub_comment_count
    )

@handle_exception
def get_sub_comment_list(article_uuid, parent_comment_id, sub_comment_offset, sub_comment_count):
  if sub_comment_offset < 0:
    raise ArgInvalid("primary comment offset is less than 0")

  if sub_comment_count < 0:
    raise ArgInvalid("primary comment count is less than 0")

  # TODO: restrict primary_comment_count and sub_comment_count below 128?

  if sub_comment_count < 0:
    raise ArgInvalid("sub comment count is less than 0")

  flag, sub_comments = Comment.find_rangeof_sub_comments_by_parent_comment_id(parent_comment_id, sub_comment_offset, sub_comment_count + 1)
  
  is_more = False
  if len(sub_comments) == sub_comment_count + 1:
    is_more = True
    del sub_comments[-1]

  if flag:
    return {
      "article_uuid": article_uuid,
      "sub_comment_list": sub_comments,
      "is_more": is_more
    }
  else:
    raise DbNotFound