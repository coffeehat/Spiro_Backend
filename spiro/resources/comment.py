from easydict import EasyDict
from flask_restful import Resource, marshal_with, fields as restful_fields
from webargs import fields as webargs_fields
from webargs.flaskparser import use_args

from ..auth.multi_auth import multi_auth
from ..common.defs import Role, Defaults
from ..common.email import email_sender_worker
from ..common.exceptions import *
from ..common.lock import r_lock, w_lock
from ..common.utils import get_utc_timestamp, MarshalJsonItem
from ..db import Comment, User

request_args = EasyDict()
request_args.get = {
  "comment_id":         webargs_fields.Integer(required=True),
}
request_args.post = {
  "article_id":         webargs_fields.Integer(required=True),
  "comment_content":    webargs_fields.String(required=True),
  "user_name":          webargs_fields.String(missing = ""),
  "user_email":         webargs_fields.String(missing = ""),
  "parent_comment_id":   webargs_fields.Integer(missing = 0),
  "to_user_id":         webargs_fields.Integer(missing = 0),
  "to_user_name":       webargs_fields.String(missing = "")
}
request_args.delete = {
  "comment_id":         webargs_fields.Integer(required=True)
}

primary_comment_response_fields_without_error = {
  "article_id":         restful_fields.Integer(default = 0),
  "user_id":            restful_fields.Integer(default = 0),
  "user_name":          restful_fields.String(default = ""),
  "comment_id":         restful_fields.Integer(default = 0),
  "comment_timestamp":  restful_fields.String(default = ""),
  "comment_content":    restful_fields.String(default = "")
}

full_comment_response_fields_without_error = {
  "parent_comment_id":  restful_fields.Integer(default = 0),
  "to_user_id":         restful_fields.Integer(default = 0),
  "to_user_name":       restful_fields.String(default = "")
}
full_comment_response_fields_without_error.update(primary_comment_response_fields_without_error)

error_response = {
  "error_code":         restful_fields.Integer(default = ErrorCode.EC_SUCCESS.value),
  "error_hint":         MarshalJsonItem(default = ""),
  "error_msg":          restful_fields.String(default = "")
}
response_fields = EasyDict()
response_fields.get = full_comment_response_fields_without_error
response_fields.get.update(error_response)
response_fields.post = response_fields.get

response_fields.delete = error_response

class CommentApi(Resource):
  @r_lock
  @use_args(request_args.get, location="query")
  @marshal_with(response_fields.get)
  def get(self, args):
    comment_id = args["comment_id"]
    return get_comment(comment_id)

  @w_lock
  @use_args(request_args.post, location="form")
  @multi_auth.login_required(role=[Role.Visitor.value, Role.Member.value, Role.Admin.value])
  @marshal_with(response_fields.post)
  def post(self, args):
    article_id          = args["article_id"]
    comment_content     = args["comment_content"]
    user_id             = multi_auth.current_user().user_id
    user_name           = multi_auth.current_user().user_name
    parent_comment_id    = args["parent_comment_id"]
    to_user_id          = args["to_user_id"]
    to_user_name        = args["to_user_name"]
    # user_email       = multi_auth.current_user()["user_email"]

    return save_comment(
      article_id, 
      user_id, 
      user_name, 
      comment_content, 
      parent_comment_id, 
      to_user_id, 
      to_user_name
    )

  @w_lock
  @use_args(request_args.delete, location="form")
  @multi_auth.login_required(role=[Role.Member.value, Role.Admin.value])
  @marshal_with(response_fields.delete)
  def delete(self, args):
    comment_id          = args["comment_id"]
    user_id             = multi_auth.current_user().user_id

    return delete_comment(comment_id, user_id)

@handle_exception
def save_comment(
  article_id, 
  user_id,
  user_name, 
  comment_content, 
  parent_comment_id, 
  to_user_id, 
  to_user_name
):
  if (not comment_content):
    raise ArgEmptyComment

  # to_user_id and to_user_name must both show up or empty
  if ((to_user_id and not to_user_name) or 
      (not to_user_id and to_user_name)):
    raise ArgInvalid
  
  # If provide to_user_id/to_user_name, parent_comment_id must be provided
  if (to_user_id and not parent_comment_id):
    raise ArgInvalid

  # TODO: check whether user_id and commit_id exists
  if (parent_comment_id):
    pass

  comment = Comment(
    article_id =        article_id,
    user_id =           user_id,
    user_name =         user_name,
    comment_content =   comment_content,
    comment_timestamp = get_utc_timestamp(),
    parent_comment_id =  parent_comment_id  if parent_comment_id else None,
    to_user_id =        to_user_id        if to_user_id       else None,
    to_user_name =      to_user_name      if to_user_name     else None
  )
  comment_id = Comment.add_comment(comment)
  flag, to_email = User.get_user_email_by_user_id(to_user_id)
  if (flag):
    email_sender_worker.send(to_email, user_name, comment_content)
  return {
    "article_id":             comment.article_id,
    "user_id":                comment.user_id,
    "user_name":              user_name,
    "comment_id":             comment_id,
    "comment_timestamp":      str(comment.comment_timestamp),
    "comment_content":        comment.comment_content,
    "parent_comment_id":      comment.parent_comment_id,
    "to_user_id":             comment.to_user_id,
    "to_user_name":           comment.to_user_name
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
      "parent_comment_id":    comment.parent_comment_id,
      "to_user_id":           comment.to_user_id,
      "to_user_name":         comment.to_user_name
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