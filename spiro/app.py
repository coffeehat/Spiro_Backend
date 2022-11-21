from flask import Flask
from flask_restful import Api

from .common.utils import singleton
from .config import config
from .resources import *

@singleton
class Server:
  def __init__(self):
    self.app = Flask(config.app_name)
    self.api = Api(self.app)

    self._add_resource()
  
  def _add_resource(self):
    self.api.add_resource(CommentList, "/" + config.version + "/comment_list")
    self.api.add_resource(Comment, "/" + config.version + "/comment")

  def run(self):
    self.app.run()
