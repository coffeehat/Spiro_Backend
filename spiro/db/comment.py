import typing
import sqlalchemy as sa

from ..db import db

class Comment(db.Model):
  comment_id            = sa.Column(sa.Integer,                 primary_key=True)
  article_id            = sa.Column(sa.Integer,                 nullable=False)
  user_id               = sa.Column(sa.ForeignKey("user.user_id"),   nullable=False)
  user_name             = sa.Column(sa.ForeignKey("user.user_name"), nullable=False)
  comment_content       = sa.Column(sa.String,                  nullable=False)
  comment_timestamp     = sa.Column(sa.Integer,                 nullable=False)

  @staticmethod
  def add_comment(comment: 'Comment'):
    ret = db.session.execute(
      sa.text(
        f"INSERT INTO {Comment.__table__.name} \
          (article_id, user_id, user_name, comment_content, comment_timestamp) \
          VALUES (:article_id, :user_id, :user_name, :comment_content, :comment_timestamp) \
          RETURNING comment_id"
      ),
      {
        "article_id":                 comment.article_id, 
        "user_id":                    comment.user_id,
        "user_name":                  comment.user_name,
        "comment_content":            comment.comment_content, 
        "comment_timestamp":          comment.comment_timestamp
      }
    ).first()
    comment_id = ret[0]
    db.session.commit()
    return comment_id

  @staticmethod
  def find_comment_by_id(comment_id) -> typing.Tuple[bool, typing.Optional['Comment']]:
    comment = db.session.execute(sa.select(Comment) \
      .where(Comment.comment_id == comment_id) \
      .limit(1)
    ).scalars().first()
    if comment:
      return True, comment,
    else:
      return False, None

  @staticmethod
  def find_rangeof_comments_by_article_id(article_id, offset, length):
    if length <= 0 or length is None:
      comments = db.session.execute(sa.select(Comment) \
        .where(Comment.article_id == article_id) \
        .order_by(Comment.comment_timestamp.desc()) \
        .offset(offset)
      ).scalars()
    else:
      comments = db.session.execute(sa.select(Comment) \
        .where(Comment.article_id == article_id) \
        .order_by(Comment.comment_timestamp.desc()) \
        .offset(offset) \
        .limit(length)
      ).scalars()
    if comments:
      return True, [comment for comment in comments]
    else:
      return False, None

  @staticmethod
  def get_comments_count_by_article_id(article_id) -> int:
    count = db.session.execute(
      sa.select(sa.func.count().label("count")) \
      .where(Comment.article_id == article_id) \
      .limit(1)
    ).first()
    return count["count"]