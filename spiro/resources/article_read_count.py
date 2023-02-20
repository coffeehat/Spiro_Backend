from easydict import EasyDict
from flask_restful import Resource, marshal_with, fields as restful_fields
from webargs import fields as webargs_fields
from webargs.flaskparser import use_args

from ..common.exceptions import *
from ..common.utils import MarshalJsonItem
from ..common.lock import article_r_lock, article_w_lock
from ..db import Article

request_args = EasyDict()
request_args.get = {
  "article_uuid":   webargs_fields.String(required=True),
  "article_link":   webargs_fields.String(required=True),
  "article_name":   webargs_fields.String(required=True)
}

request_args.post = request_args.get

response_fields = EasyDict()
response_fields.get = {
  "article_uuid":   restful_fields.String(default = ""),
  "count":        restful_fields.Integer(default = 0),
  "error_code":   restful_fields.Integer(default = ErrorCode.EC_SUCCESS.value),
  "error_hint":   MarshalJsonItem(default = ""),
  "error_msg":    restful_fields.String(default = "")
}

response_fields.post = response_fields.get

class ArticleReadCountApi(Resource):
  @article_r_lock
  @use_args(request_args.get, location="query")
  @marshal_with(response_fields.get)
  def get(self, args):
    article_uuid  = args["article_uuid"]
    article_link  = args["article_link"]
    article_name  = args["article_name"]
    return get_article_read_count(article_uuid, article_link, article_name)

  @article_w_lock
  @use_args(request_args.post, location="form")
  @marshal_with(response_fields.post)
  def post(self, args):
    article_uuid  = args["article_uuid"]
    article_link  = args["article_link"]
    article_name  = args["article_name"]
    return incre_article_read_count(article_uuid, article_link, article_name)

@handle_exception
def get_article_read_count(article_uuid, article_link, article_name):
  flag, count = Article.get_article_read_count_by_uuid(article_uuid)
  if flag:
    return {
      "article_uuid": article_uuid,
      "count": count
    }
  else:
    Article.add_article(
      Article(
        article_uuid = article_uuid,
        article_link = article_link,
        article_name = article_name,
        article_read_count = 1
      )
    )
    return {
      "article_uuid": article_uuid,
      "count": 1
    }

@handle_exception
def incre_article_read_count(article_uuid, article_link, article_name):
  article = Article.incre_article_read_count_by_uuid(article_uuid)
  if article is None:
    Article.add_article(
      Article(
        article_uuid = article_uuid,
        article_link = article_link,
        article_name = article_name,
        article_read_count = 1
      )
    )
    return {
      "article_uuid": article_uuid,
      "count": 1
    }
  elif article.article_name != article_name:
    Article.update_article_name_by_uuid(article_uuid, article_name)
  return {
    "article_uuid": article_uuid,
    "count": article.article_read_count
  }