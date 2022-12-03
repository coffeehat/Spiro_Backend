from flask import Flask
from flask_restful import Api
from flask_cors import CORS

from .common.utils import singleton
from .config import config
from .resources import *

from .db import db, User, Comment

# @singleton
class Server:
  def __init__(self):
    self.app = Flask(config.app_name)
    CORS(self.app, supports_credentials=True)
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
    self.api.add_resource(CommentListApi, "/" + config.version + "/comment_list")
    self.api.add_resource(CommentApi, "/" + config.version + "/comment")
    self.api.add_resource(UserApi, "/" + config.version + "/user")

  def run(self):
    self.app.run()
