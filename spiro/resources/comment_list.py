from easydict import EasyDict
from copy import deepcopy
from flask_restful import Resource, marshal_with, fields as restful_fields
from webargs import fields as webargs_fields
from webargs.flaskparser import use_args

from .comment import primary_comment_response_fields_without_error, \
  full_comment_response_fields_without_error

from ..common.defs import CommentListGetMethod
from ..common.exceptions import *
from ..common.utils import MarshalJsonItem, parse_comments_and_get_is_more_status
from ..common.lock import r_lock
from ..db import Comment

request_args = EasyDict()
request_args.get = {
  "article_uuid":                   webargs_fields.String(required=True),
  "primary_comment_count":          webargs_fields.Int(required=True),
  "sub_comment_count":              webargs_fields.Int(missing=5),
  "method":                         webargs_fields.Int(required=True),

  # Special Argument for method COUNT_FROM_OFFSET
  "primary_start_comment_offset":   webargs_fields.Int(),

  # Special Argument for method COUNT_FROM_COMMENT_ID
  "primary_start_comment_id":       webargs_fields.Int(),
  # Whether to return comments newer than primary_start_comment_id (inclusive)
  "is_newer":                       webargs_fields.Boolean(missing=False)
  
}

primary_comment_response_fields = deepcopy(primary_comment_response_fields_without_error)
primary_comment_response_fields["sub_comment_list"] = \
  restful_fields.List(restful_fields.Nested(full_comment_response_fields_without_error))
primary_comment_response_fields["is_more_old"] = \
  restful_fields.Boolean()
primary_comment_response_fields["is_more_new"] = \
  restful_fields.Boolean()

response_fields = EasyDict()
response_fields.get = {
  "article_uuid": restful_fields.String(),
  "comment_list": restful_fields.List(restful_fields.Nested(primary_comment_response_fields)),
  "is_more_old":  restful_fields.Boolean(),
  "is_more_new":  restful_fields.Boolean(),
  "error_code":   restful_fields.Integer(default = ErrorCode.EC_SUCCESS.value),
  "error_hint":   MarshalJsonItem(default = ""),
  "error_msg":    restful_fields.String(default = "")
}

class CommentListApi(Resource):
  @r_lock
  @use_args(request_args.get, location="query")
  @marshal_with(response_fields.get)
  def get(self, args):
    return handle_request(args)

@handle_exception
def handle_request(args):
  article_uuid                    = args["article_uuid"]
  primary_comment_count           = args["primary_comment_count"]
  sub_comment_count               = args["sub_comment_count"]
  method                          = args["method"]

  if method == CommentListGetMethod.COUNT_FROM_OFFSET.value:
    primary_start_comment_offset  = args["primary_start_comment_offset"]
    return get_comment_list_by_offset(
      article_uuid,
      primary_start_comment_offset,
      primary_comment_count,
      sub_comment_count
    )
  elif method == CommentListGetMethod.COUNT_FROM_COMMENT_ID.value:
    primary_start_comment_id      = args["primary_start_comment_id"]
    is_newer                      = args["is_newer"]
    return get_comment_list_by_id(
      article_uuid,
      primary_start_comment_id,
      primary_comment_count,
      sub_comment_count,
      is_newer
    )
  else:
    raise ArgInvalid

def get_comment_list_by_offset(article_uuid, primary_start_comment_offset, primary_comment_count, sub_comment_count):
  if primary_start_comment_offset < 0:
    raise ArgInvalid("primary comment offset is less than 0")

  if primary_comment_count < 0:
    raise ArgInvalid("primary comment count is less than 0")

  # TODO: restrict primary_comment_count and sub_comment_count below 128?

  if sub_comment_count < 0:
    raise ArgInvalid("sub comment count is less than 0")

  flag, comments, sub_comments = Comment.find_rangeof_comments_by_offset_and_article_uuid(
    article_uuid, 
    primary_start_comment_offset, 
    primary_comment_count + 1, 
    sub_comment_count + 1
  )
  if flag:
    primary_is_more_old = False
    primary_is_more_new = primary_start_comment_offset != 0
    primary_ids_to_be_excluded = set()
    if len(comments) == primary_comment_count + 1:
      primary_is_more_old = True
      primary_ids_to_be_excluded.add(comments[-1].comment_id)
      del comments[-1]

    _compose_primary_and_sub_comments(comments, sub_comments, primary_ids_to_be_excluded, sub_comment_count)
  
    return {
      "article_uuid"    : article_uuid,
      "comment_list"    : comments,
      "is_more_new"     : primary_is_more_new, 
      "is_more_old"     : primary_is_more_old
    }
  else:
    return {
      "article_uuid"    : article_uuid,
      "comment_list"    : [],
      "is_more_new"     : False, 
      "is_more_old"     : False
    }

def get_comment_list_by_id(article_uuid, primary_start_comment_id, primary_comment_count, sub_comment_count, is_newer):
  if primary_comment_count < 0:
    raise ArgInvalid("primary comment count is less than 0")

  # TODO: restrict primary_comment_count and sub_comment_count below 128?

  if sub_comment_count < 0:
    raise ArgInvalid("sub comment count is less than 0")

  flag, comments, sub_comments = Comment.find_rangeof_comments_by_comment_id_and_article_uuid(
    article_uuid, 
    primary_start_comment_id, 
    primary_comment_count + 2, 
    sub_comment_count + 1, 
    is_newer
  )

  if flag:
    primary_ids_to_be_excluded, \
    primary_is_more_old, \
    primary_is_more_new = parse_comments_and_get_is_more_status(
      comments,
      primary_start_comment_id,
      primary_comment_count,
      is_newer
    )

    _compose_primary_and_sub_comments(comments, sub_comments, primary_ids_to_be_excluded, sub_comment_count)

    return {
      "article_uuid"    : article_uuid,
      "comment_list"    : comments,
      "is_more_new"     : primary_is_more_new, 
      "is_more_old"     : primary_is_more_old
    }
  else:
    return {
      "article_uuid"    : article_uuid,
      "comment_list"    : [],
      "is_more_new"     : False, 
      "is_more_old"     : False
    } 

def _compose_primary_and_sub_comments(comments, sub_comments, primary_ids_to_be_excluded, sub_comment_count):
  comment_id_mapping = {}
  for i, comment in enumerate(comments):
    comment.sub_comment_list = []
    comment_id_mapping[comment.comment_id] = i

  for sub_comment in sub_comments:
    if sub_comment.parent_comment_id in primary_ids_to_be_excluded:
      continue
    index = comment_id_mapping[sub_comment.parent_comment_id]
    comments[index].sub_comment_list.append(sub_comment)

  for comment in comments:
    comment.is_more_new = False
    if comment.sub_comment_list:
      comment.is_more_old = len(comment.sub_comment_list) == sub_comment_count + 1
      if comment.is_more_old:
        del comment.sub_comment_list[-1]
    else:
      comment.is_more_old = False