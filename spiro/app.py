from flask import Flask
from flask_restful import Api
from flask_cors import CORS

from .common.utils import singleton
from .config import config
from .resources import *

@singleton
class Server:
  def __init__(self):
    self.app = Flask(config.app_name)
    CORS(self.app, supports_credentials=True)
    self.api = Api(self.app)

    self._add_resource()
  
  def _add_resource(self):
    self.api.add_resource(CommentList, "/" + config.version + "/comment_list")
    self.api.add_resource(Comment, "/" + config.version + "/comment")
    self.api.add_resource(UserRegister, "/" + config.version + "/user_register")

  def run(self):
    self.app.run()
