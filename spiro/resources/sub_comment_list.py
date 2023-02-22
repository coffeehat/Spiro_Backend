from easydict import EasyDict
from copy import deepcopy
from flask_restful import Resource, marshal_with, fields as restful_fields
from webargs import fields as webargs_fields
from webargs.flaskparser import use_args

from .comment import full_comment_response_fields_without_error

from ..common.defs import CommentListGetMethod
from ..common.exceptions import *
from ..common.lock import r_lock
from ..common.utils import MarshalJsonItem, parse_comments_and_get_is_more_status
from ..db import Comment

request_args = EasyDict()
request_args.get = {
  "article_uuid"                        : webargs_fields.String(required=True),
  "parent_comment_id"                   : webargs_fields.Int(required=True),
  "sub_comment_count"                   : webargs_fields.Int(required=True),
  "method"                              : webargs_fields.Int(required=True),

  # Special Argument for method COUNT_FROM_OFFSET
  "sub_start_comment_offset"            : webargs_fields.Int(),

  # Special Argument for method COUNT_FROM_COMMENT_ID
  "sub_start_comment_id"                : webargs_fields.Int(),
  # Whether to return comments newer than sub_start_comment_id (inclusive)
  "is_newer"                            : webargs_fields.Boolean(missing=False)
}

response_fields = EasyDict()
response_fields.get = {
  "article_uuid"                        : restful_fields.String(),
  "sub_comment_list"                    : restful_fields.List(
    restful_fields.Nested(full_comment_response_fields_without_error)
  ),
  "is_more_old"                         : restful_fields.Boolean(),
  "is_more_new"                         : restful_fields.Boolean(),
  "error_code"                          : restful_fields.Integer(default = ErrorCode.EC_SUCCESS.value),
  "error_hint"                          : MarshalJsonItem(default = ""),
  "error_msg"                           : restful_fields.String(default = "")
}

class SubCommentListApi(Resource):
  @r_lock
  @use_args(request_args.get, location="query")
  @marshal_with(response_fields.get)
  def get(self, args):
    return handle_request(args)

@handle_exception
def handle_request(args):
  article_uuid                        = args["article_uuid"]
  parent_comment_id                   = args["parent_comment_id"]
  sub_comment_count                   = args["sub_comment_count"]
  method                              = args["method"]

  if method == CommentListGetMethod.COUNT_FROM_OFFSET.value:
    sub_start_comment_offset          = args["sub_start_comment_offset"]
    return get_sub_comment_list_by_offset(
      article_uuid,
      parent_comment_id,
      sub_start_comment_offset,
      sub_comment_count
    )
  elif method == CommentListGetMethod.COUNT_FROM_COMMENT_ID.value:
    sub_start_comment_id              = args["sub_start_comment_id"]
    is_newer                          = args["is_newer"]
    return get_sub_comment_list_by_id(
      article_uuid, 
      parent_comment_id, 
      sub_start_comment_id, 
      sub_comment_count, 
      is_newer
    )
  else:
    raise ArgInvalid

def get_sub_comment_list_by_offset(article_uuid, parent_comment_id, sub_start_comment_offset, sub_comment_count):
  if sub_start_comment_offset < 0:
    raise ArgInvalid("sub comment offset is less than 0")

  # TODO: restrict primary_comment_count and sub_comment_count below 128?

  if sub_comment_count < 0:
    raise ArgInvalid("sub comment count is less than 0")

  flag, sub_comments = Comment.find_rangeof_sub_comments_by_parent_comment_id(parent_comment_id, sub_start_comment_offset, sub_comment_count + 1)
  
  is_more_old = False
  if len(sub_comments) == sub_comment_count + 1:
    is_more_old = True
    del sub_comments[-1]

  if flag:
    return {
      "article_uuid"                    : article_uuid,
      "sub_comment_list"                : sub_comments,
      "is_more_old"                     : is_more_old,
      "is_more_new"                     : False
    }
  else:
    return {
      "article_uuid"                    : article_uuid,
      "sub_comment_list"                : [],
      "is_more_old"                     : False,
      "is_more_new"                     : False
    }

def get_sub_comment_list_by_id(article_uuid, parent_comment_id, sub_start_comment_id, sub_comment_count, is_newer):
  if sub_comment_count < 0:
    raise ArgInvalid("sub comment count is less than 0")

  flag, sub_comments = Comment.find_rangeof_sub_comments_by_comment_id_and_article_uuid(
    article_uuid,
    parent_comment_id,
    sub_start_comment_id,
    sub_comment_count + 2,
    is_newer
  )

  if flag:
    _, sub_is_more_old, sub_is_more_new = parse_comments_and_get_is_more_status(
      sub_comments,
      sub_start_comment_id,
      sub_comment_count,
      is_newer
    )

    return {
      "article_uuid"                    : article_uuid,
      "sub_comment_list"                : sub_comments,
      "is_more_old"                     : sub_is_more_old,
      "is_more_new"                     : sub_is_more_new
    }
  else:
    return {
      "article_uuid"                    : article_uuid,
      "sub_comment_list"                : [],
      "is_more_old"                     : False,
      "is_more_new"                     : False
    }