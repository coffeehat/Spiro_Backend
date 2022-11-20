from flask_restful import Resource, marshal_with, fields as restful_fields
from webargs import fields as webargs_fields
from webargs.flaskparser import use_args

from ..common.time import get_current_time

from .comment import resource_fields

query_args = {
  "article_id":   webargs_fields.Int(required=True),
  "range_start":  webargs_fields.Int(required=True),
  "range_end":    webargs_fields.Int(required=True)
}

resource_fields = {
  "article_id":   restful_fields.Integer(),
  "comment_list": restful_fields.List(restful_fields.Nested(resource_fields))
}

class CommentList(Resource):
  @use_args(query_args, location="form")
  @marshal_with(resource_fields)
  def get(self, args):
    article_id  = args["article_id"]
    range_start = args["range_start"] if not args["range_start"] is None else 0
    range_end   = args["range_end"]   if not args["range_end"]   is None else 0
    
    comment_list = get_comment_list(article_id, range_start, range_end)
    return {
      "article_id": article_id,
      "comment_list": comment_list
    }

# Data query function
def get_comment_list(article_id, range_start = 0, range_end = -1):
  demo1 = {
    "article_id":   0,
    "user_id":      0,
    "user_name":    "coffeehat",
    "comment_time": get_current_time(),
    "comment":      "Hello World!"
  }
  demo2 = {
    "article_id":   1,
    "user_id":      0,
    "user_name":    "coffeehat",
    "comment_time": get_current_time(),
    "comment":      "Hello Flask!"
  }
  return [demo1, demo2]