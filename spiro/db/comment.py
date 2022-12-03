import sqlalchemy as sa

from ..db import db

class Comment(db.Model):
  id            = sa.Column(sa.Integer,               primary_key=True)
  article_id    = sa.Column(sa.Integer,               nullable=False)
  user_id       = sa.Column(sa.ForeignKey("user.id"), nullable=False)
  comment       = sa.Column(sa.String,                nullable=False)
  timestamp     = sa.Column(sa.Integer,           nullable=False)

  @staticmethod
  def add_comment(comment):
    ret = db.session.execute(
      sa.text(
        f"INSERT INTO {Comment.__table__.name} \
          (article_id, user_id, comment, timestamp) \
          VALUES (:article_id, :user_id, :comment, :timestamp) \
          RETURNING id"
      ),
      {
        "article_id":         comment.article_id, 
        "user_id":            comment.user_id, 
        "comment":            comment.comment, 
        "timestamp":          comment.timestamp
      }
    ).first()
    comment_id = ret[0]
    db.session.commit()
    return comment_id

  @staticmethod
  def find_comment_by_id(id):
    comment = db.session.execute(sa.select(Comment) \
      .where(Comment.id == id) \
      .limit(1)
    ).scalars().first()
    if comment:
      return True, comment,
    else:
      return False, None