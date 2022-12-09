import sqlalchemy as sa

from ..db import db

class Comment(db.Model):
  id            = sa.Column(sa.Integer,                 primary_key=True)
  article_id    = sa.Column(sa.Integer,                 nullable=False)
  user_id       = sa.Column(sa.ForeignKey("user.id"),   nullable=False)
  user_name     = sa.Column(sa.ForeignKey("user.name"), nullable=False)
  comment       = sa.Column(sa.String,                  nullable=False)
  timestamp     = sa.Column(sa.Integer,                 nullable=False)

  @staticmethod
  def add_comment(comment):
    ret = db.session.execute(
      sa.text(
        f"INSERT INTO {Comment.__table__.name} \
          (article_id, user_id, user_name, comment, timestamp) \
          VALUES (:article_id, :user_id, :user_name, :comment, :timestamp) \
          RETURNING id"
      ),
      {
        "article_id":         comment.article_id, 
        "user_id":            comment.user_id,
        "user_name":          comment.user_name,
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

  # TODO: I don't like the implementation here, consider to change this
  @staticmethod
  def find_rangeof_comments_by_article_id_with_output_name(article_id, offset, length):
    if length < 0 or length is None:
      comments = db.session.query(sa.select(
        Comment.id.label("comment_id"),
        Comment.article_id.label("article_id"),
        Comment.user_id.label("userid"),
        Comment.user_name.label("username"),
        Comment.comment.label("comment"),
        Comment.timestamp.label("comment_time")
      ) \
        .where(Comment.article_id == article_id) \
        .order_by(Comment.timestamp.desc()) \
        .offset(offset)
      )
    else:
      comments = db.session.execute(sa.select(
        Comment.id.label("comment_id"),
        Comment.article_id.label("article_id"),
        Comment.user_id.label("userid"),
        Comment.user_name.label("username"),
        Comment.comment.label("comment"),
        Comment.timestamp.label("comment_time")
      ) \
        .where(Comment.article_id == article_id) \
        .order_by(Comment.timestamp.desc()) \
        .offset(offset) \
        .limit(length)
      )
    if comments:
      return True, [comment for comment in comments]
    else:
      return False, None

  @staticmethod
  def find_rangeof_comments_by_article_id(article_id, offset, length):
    if length < 0 or length is None:
      comments = db.session.execute(sa.select(Comment) \
        .where(Comment.article_id == article_id) \
        .order_by(Comment.timestamp.desc()) \
        .offset(offset)
      ).scalars()
    else:
      comments = db.session.execute(sa.select(Comment) \
        .where(Comment.article_id == article_id) \
        .order_by(Comment.timestamp.desc()) \
        .offset(offset) \
        .limit(length)
      ).scalars()
    if comments:
      return True, [comment for comment in comments]
    else:
      return False, None

  @staticmethod
  def get_comments_count_by_article_id(article_id):
    count = db.session.execute(
      sa.select(sa.func.count().label("count")) \
      .where(Comment.article_id == article_id) \
      .limit(1)
    ).first()
    return count["count"]