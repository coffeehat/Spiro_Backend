from easydict import EasyDict
from flask_restful import Resource, marshal_with, fields as restful_fields
from webargs import fields as webargs_fields
from webargs.flaskparser import use_args

from ..auth.multi_auth import multi_auth
from ..common.defs import Role, Defaults
from ..common.exceptions import *
from ..common.utils import get_time_stamp, MarshalJsonItem
from ..db import User, Comment

request_args = EasyDict()
request_args.get = {
  "comment_id":   webargs_fields.Integer(required=True),
}
request_args.post = {
  "article_id":   webargs_fields.Integer(required=True),
  "comment":      webargs_fields.String(required=True),
  "username":     webargs_fields.String(),
  "email":        webargs_fields.String()
}

response_fields = EasyDict()
response_fields.get = {
  "article_id":   restful_fields.Integer(default = 0),
  "username":     restful_fields.String(default = ""),
  "comment_id":   restful_fields.Integer(default = 0),
  "comment_time": restful_fields.String(default = ""),
  "comment":      restful_fields.String(default = ""),
  "error_code":   restful_fields.Integer(default = ErrorCode.EC_SUCCESS.value),
  "error_hint":   MarshalJsonItem(default = ""),
  "error_msg":    restful_fields.String(default = "")
}
response_fields.post = response_fields.get

class CommentApi(Resource):
  @use_args(request_args.get, location="form")
  @marshal_with(response_fields.get)
  def get(self, args):
    comment_id = args["comment_id"]
    return get_comment(comment_id)

  @use_args(request_args.post, location="form")
  @multi_auth.login_required(role=[Role.Visitor.value, Role.Member.value, Role.Admin.value])
  @marshal_with(response_fields.post)
  def post(self, args):
    article_id  = args["article_id"]
    comment     = args["comment"]
    user_id     = multi_auth.current_user().id
    username    = multi_auth.current_user().name
    # email       = multi_auth.current_user()["email"]

    return save_comment(article_id, user_id, username, comment)

@handle_exception
def save_comment(article_id, user_id, username, comment):
  comment = Comment(
    article_id = article_id,
    user_id = user_id,
    comment = comment,
    timestamp = get_time_stamp()
  )
  comment_id = Comment.add_comment(comment)
  return {
    "article_id":   comment.article_id,
    "username":     username,
    "comment_id":   comment_id,
    "comment_time": str(comment.timestamp),
    "comment":      comment.comment,
  }

@handle_exception
def get_comment(comment_id):
  flag1, comment = Comment.find_comment_by_id(comment_id)
  flag2, user = User.find_user_by_id(comment.user_id)
  if flag1:
    return {
      "article_id":   comment.article_id,
      "username":     user.name if flag2 else Defaults.UserNameInactive.value,
      "comment_id":   comment.id,
      "comment_time": comment.timestamp,
      "comment":      comment.comment,
    }
  else:
    raise DbNotFound(error_msg = f"Cannot find comment by comment id: {comment_id}")