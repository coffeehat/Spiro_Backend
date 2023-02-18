from flask import Flask
from flask_restful import Api
from flask_cors import CORS
from waitress import serve

from .common.email import email_sender_worker
from .config import config
from .resources import *

from .db import db

# @singleton
class Server:
  def __init__(self):
    self.app = Flask(config.app_name)
    CORS(
      self.app,
      supports_credentials=True
    )
    self.api = Api(self.app)

    # Database related
    self.app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///comments.db"
    self.app.config['SQLALCHEMY_ECHO'] = True
    db.init_app(self.app)

    with self.app.app_context():
      db.create_all()

    # Resource bindings
    self._add_resource()
  
  def _add_resource(self):
    self.api.add_resource(CommentCountApi, "/" + config.version + "/comment_count")
    self.api.add_resource(CommentListApi, "/" + config.version + "/comment_list")
    self.api.add_resource(CommentApi, "/" + config.version + "/comment")
    self.api.add_resource(UserApi, "/" + config.version + "/user")
    self.api.add_resource(TokenCheckApi, "/" + config.version + "/token_check")
    self.api.add_resource(SubCommentListApi, "/" + config.version + "/sub_comment_list")

  def run(self):
    email_sender_worker.run()
    serve(
      self.app, 
      host=config.network.listen_ip, 
      port=config.network.port
    )
    email_sender_worker.terminate()
