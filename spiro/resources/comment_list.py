from easydict import EasyDict
from copy import deepcopy
from flask_restful import Resource, marshal_with, fields as restful_fields
from webargs import fields as webargs_fields
from webargs.flaskparser import use_args

from .comment import primary_comment_response_fields_without_error, \
  full_comment_response_fields_without_error

from ..common.exceptions import *
from ..common.utils import MarshalJsonItem
from ..db import Comment

request_args = EasyDict()
request_args.get = {
  "article_id":               webargs_fields.Int(required=True),
  "primary_comment_offset":   webargs_fields.Int(required=True),
  "primary_comment_count":    webargs_fields.Int(required=True),
  "sub_comment_count":        webargs_fields.Int(missing=3)
}

primary_comment_response_fields = deepcopy(primary_comment_response_fields_without_error)
primary_comment_response_fields["sub_comment_list"] = \
  restful_fields.List(restful_fields.Nested(full_comment_response_fields_without_error))

response_fields = EasyDict()
response_fields.get = {
  "article_id":   restful_fields.Integer(),
  "comment_list": restful_fields.List(restful_fields.Nested(primary_comment_response_fields)),
  "error_code":   restful_fields.Integer(default = ErrorCode.EC_SUCCESS.value),
  "error_hint":   MarshalJsonItem(default = ""),
  "error_msg":    restful_fields.String(default = "")
}

class CommentListApi(Resource):
  @use_args(request_args.get, location="query")
  @marshal_with(response_fields.get)
  def get(self, args):
    article_id                  = args["article_id"]
    primary_comment_offset      = args["primary_comment_offset"]
    primary_comment_count       = args["primary_comment_count"]
    sub_comment_count           = args["sub_comment_count"]
    
    return get_comment_list(
      article_id,
      primary_comment_offset,
      primary_comment_count,
      sub_comment_count
    )

@handle_exception
def get_comment_list(article_id, primary_comment_offset, primary_comment_count, sub_comment_count):
  if primary_comment_offset < 0:
    raise ArgInvalid("primary comment offset is less than 0")

  if primary_comment_count < 0:
    raise ArgInvalid("primary comment count is less than 0")

  # TODO: restrict primary_comment_count and sub_comment_count below 128?

  if sub_comment_count < 0:
    raise ArgInvalid("sub comment count is less than 0")

  flag, comments, sub_comments = Comment.find_rangeof_comments_by_article_id(article_id, primary_comment_offset, primary_comment_count, sub_comment_count)
  comment_id_mapping = {}
  for i, comment in enumerate(comments):
    comment.sub_comment_list = []
    comment_id_mapping[comment.comment_id] = i

  for sub_comment in sub_comments:
    index = comment_id_mapping[sub_comment.parent_comment_id]
    comments[index].sub_comment_list.append(sub_comment)
  
  if flag:
    return {
      "article_id": article_id,
      "comment_list": comments
    }
  else:
    raise DbNotFound