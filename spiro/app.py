from flask import Flask
from flask_restful import Api
from flask_cors import CORS
from waitress import serve

from .common.email import init_email_worker
from .config import SpiroConfig, check_config
from .resources import *

from .db import db

# @singleton
class Server:
  def __init__(self):
    check_config()
    self.app = Flask(SpiroConfig.app_name)
    CORS(
      self.app,
      supports_credentials=True
    )
    self.api = Api(self.app)

    # Database related
    self.app.config["SQLALCHEMY_DATABASE_URI"] = SpiroConfig.db.url
    self.app.config['SQLALCHEMY_ECHO'] = SpiroConfig.db.is_debug
    db.init_app(self.app)

    with self.app.app_context():
      db.create_all()

    # Resource bindings
    self._add_resource()
  
  def _add_resource(self):
    self.api.add_resource(CommentCountApi,      "/" + SpiroConfig.version + "/comment_count")
    self.api.add_resource(CommentListApi,       "/" + SpiroConfig.version + "/comment_list")
    self.api.add_resource(CommentApi,           "/" + SpiroConfig.version + "/comment")
    self.api.add_resource(UserApi,              "/" + SpiroConfig.version + "/user")
    self.api.add_resource(TokenCheckApi,        "/" + SpiroConfig.version + "/token_check")
    self.api.add_resource(SubCommentListApi,    "/" + SpiroConfig.version + "/sub_comment_list")
    self.api.add_resource(ArticleReadCountApi,  "/" + SpiroConfig.version + "/article_read_count")
    self.api.add_resource(AnchorCommentListApi, "/" + SpiroConfig.version + "/anchor_comment_list")

    if SpiroConfig.email.enabled:
      self.api.add_resource(EmailVerificationApi, "/" + SpiroConfig.version + "/email_verify/<string:veri_id>")

  def run(self):
    if SpiroConfig.email.enabled:
      email_worker = init_email_worker()
      email_worker.run()

    serve(
      self.app, 
      host=SpiroConfig.network.listen_ip, 
      port=SpiroConfig.network.port
    )

    if SpiroConfig.email.enabled: 
      email_worker.terminate()
