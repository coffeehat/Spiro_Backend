from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()

from .user    import User
from .comment import Comment
from .article import Article