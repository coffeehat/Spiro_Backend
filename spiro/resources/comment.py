from flask_restful import Resource, marshal_with, fields as restful_fields
from webargs import fields as webargs_fields
from webargs.flaskparser import use_args

resource_fields = {
  "article_id":   restful_fields.Integer(),
  "user_id":      restful_fields.Integer(),
  "user_name":    restful_fields.String(),
  "comment_time": restful_fields.DateTime(dt_format="rfc822"),
  "comment":      restful_fields.String()
}

class Comment(Resource):
  pass