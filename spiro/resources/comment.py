from easydict import EasyDict
from flask_restful import Resource, marshal_with, fields as restful_fields
from webargs import fields as webargs_fields
from webargs.flaskparser import use_args

from ..auth.multi_auth import multi_auth
from ..common.defs import Role, Defaults
from ..common.exceptions import *
from ..common.utils import get_utc_timestamp, MarshalJsonItem
from ..db import Comment

request_args = EasyDict()
request_args.get = {
  "comment_id":         webargs_fields.Integer(required=True),
}
request_args.post = {
  "article_id":         webargs_fields.Integer(required=True),
  "comment_content":    webargs_fields.String(required=True),
  "user_name":          webargs_fields.String(),
  "user_email":         webargs_fields.String()
}
request_args.delete = {
  "comment_id":         webargs_fields.Integer(required=True)
}

comment_response_fields_without_error = {
  "article_id":         restful_fields.Integer(default = 0),
  "user_id":            restful_fields.Integer(default = 0),
  "user_name":          restful_fields.String(default = ""),
  "comment_id":         restful_fields.Integer(default = 0),
  "comment_timestamp":  restful_fields.String(default = ""),
  "comment_content":    restful_fields.String(default = ""),
}
error_response = {
  "error_code":         restful_fields.Integer(default = ErrorCode.EC_SUCCESS.value),
  "error_hint":         MarshalJsonItem(default = ""),
  "error_msg":          restful_fields.String(default = "")
}
response_fields = EasyDict()
response_fields.get = comment_response_fields_without_error
response_fields.get.update(error_response)
response_fields.post = response_fields.get

response_fields.delete = error_response

class CommentApi(Resource):
  @use_args(request_args.get, location="query")
  @marshal_with(response_fields.get)
  def get(self, args):
    comment_id = args["comment_id"]
    return get_comment(comment_id)

  @use_args(request_args.post, location="form")
  @multi_auth.login_required(role=[Role.Visitor.value, Role.Member.value, Role.Admin.value])
  @marshal_with(response_fields.post)
  def post(self, args):
    article_id          = args["article_id"]
    comment_content     = args["comment_content"]
    user_id             = multi_auth.current_user().user_id
    user_name           = multi_auth.current_user().user_name
    # user_email       = multi_auth.current_user()["user_email"]

    return save_comment(article_id, user_id, user_name, comment_content)

  @use_args(request_args.delete, location="form")
  @multi_auth.login_required(role=[Role.Member.value, Role.Admin.value])
  @marshal_with(response_fields.delete)
  def delete(self, args):
    comment_id          = args["comment_id"]
    user_id             = multi_auth.current_user().user_id

    return delete_comment(comment_id, user_id)

@handle_exception
def save_comment(article_id, user_id, user_name, comment_content):
  if (not comment_content):
    raise ArgEmptyComment

  comment = Comment(
    article_id = article_id,
    user_id = user_id,
    user_name = user_name,
    comment_content = comment_content,
    comment_timestamp = get_utc_timestamp()
  )
  comment_id = Comment.add_comment(comment)
  return {
    "article_id":             comment.article_id,
    "user_id":                comment.user_id,
    "user_name":              user_name,
    "comment_id":             comment_id,
    "comment_timestamp":      str(comment.comment_timestamp),
    "comment_content":        comment.comment_content,
  }

@handle_exception
def get_comment(comment_id):
  flag1, comment = Comment.find_comment_by_id(comment_id)
  if flag1:
    return {
      "article_id":           comment.article_id,
      "user_id":              comment.user_id,
      "user_name":            comment.user_name,
      "comment_id":           comment.comment_id,
      "comment_timestamp":    comment.comment_timestamp,
      "comment_content":      comment.comment_content,
    }
  else:
    raise DbNotFound(error_msg = f"Cannot find comment by comment id: {comment_id}")

@handle_exception
def delete_comment(comment_id, user_id):
  count = Comment.delete_comment_with_user_check(comment_id, user_id)
  if count == 1:
    return {}
  elif count == 0:
    raise CommentUserDontMatch
  else:
    # TODO: add log here, this should be impossible
    raise InternalError