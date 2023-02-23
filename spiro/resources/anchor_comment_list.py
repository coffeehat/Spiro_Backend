import re

from easydict import EasyDict
from flask_restful import Resource, marshal_with, fields as restful_fields
from webargs import fields as webargs_fields
from webargs.flaskparser import use_args

from .comment_list import response_fields
from ..common.exceptions import *
from ..common.lock import r_lock
from ..common.utils import compose_primary_and_sub_comments
from ..db import Comment

anchor_pattern = re.compile("spirorips_([ps])_([0-9]+)")

request_args = EasyDict()
request_args.get = {
  "article_uuid"                        : webargs_fields.String(required=True),
  "anchor"                              : webargs_fields.String(required=True),
  "sub_comment_count"                   : webargs_fields.Int(missing=5),
  "primary_single_side_comment_count"   : webargs_fields.Int(missing=2),
  "primary_single_side_sub_comment_count"
                                        : webargs_fields.Int(missing=2)
}

class AnchorCommentListApi(Resource):
  @r_lock
  @use_args(request_args.get, location="query")
  @marshal_with(response_fields.get)
  def get(self, args):
    return handle_request(args)

@handle_exception
def handle_request(args):
  article_uuid                          = args["article_uuid"]
  anchor                                = args["anchor"]
  sub_comment_count                     = args["sub_comment_count"]
  primary_single_side_comment_count     = args["primary_single_side_comment_count"]
  primary_single_side_sub_comment_count = args["primary_single_side_sub_comment_count"]

  is_primary, comment_id = parse_anchor(anchor)
  if is_primary:
    return get_primary_comment(
      article_uuid,
      comment_id,
      primary_single_side_comment_count,
      sub_comment_count
    )
  else:
    pass

def get_primary_comment(
  article_uuid, 
  primary_start_comment_id, 
  primary_single_side_comment_count, 
  sub_comment_count
):
  if primary_single_side_comment_count < 0:
    raise ArgInvalid("primary comment count is less than 0")

  # TODO: restrict primary_comment_count and sub_comment_count below 128?

  if sub_comment_count < 0:
    raise ArgInvalid("sub comment count is less than 0")

  flag, comments, sub_comments \
    = Comment.find_rangeof_comments_bilateral_by_comment_id_and_article_uuid(
    article_uuid,
    primary_start_comment_id,
    primary_single_side_comment_count + 1,
    sub_comment_count + 1
  )

  if flag:
    primary_is_more_old = False
    primary_is_more_new = False
    primary_ids_to_be_excluded = set()
    if len([comment for comment in comments if comment.comment_id > primary_start_comment_id]) \
      == primary_single_side_comment_count + 1:
      primary_is_more_new = True
      primary_ids_to_be_excluded.add(comments[0].comment_id)
      del comments[0]
    if len([comment for comment in comments if comment.comment_id < primary_start_comment_id]) \
      == primary_single_side_comment_count + 1:
      primary_is_more_old = True
      primary_ids_to_be_excluded.add(comments[-1].comment_id)
      del comments[-1]

    compose_primary_and_sub_comments(comments, sub_comments, primary_ids_to_be_excluded, sub_comment_count)

    return {
      "article_uuid"    : article_uuid,
      "comment_list"    : comments,
      "is_more_new"     : primary_is_more_new, 
      "is_more_old"     : primary_is_more_old
    }
  else:
    raise DbNotFound

def parse_anchor(anchor):
  """
    The format of anchor should be:
      spiro_{p or s}_{id}
    
    e.g.
      spirorips_p_4 - a primary comment whose id is 4
      spirorips_s_9 - a sub comment whose id is 9
  """
  o = re.match(anchor_pattern, anchor)
  if o:
    comment_type = o.group(1)
    comment_id = int(o.group(2))
    return comment_type == "p", comment_id
  else:
    # TODO: Add new exception called invalid anchor
    raise ArgInvalid
