import typing
import sqlalchemy as sa

from ..db import db

class Comment(db.Model):
  comment_id            = sa.Column(sa.Integer,                           primary_key=True)
  article_id            = sa.Column(sa.Integer,                           nullable=False)
  user_id               = sa.Column(sa.ForeignKey("user.user_id"),        nullable=False)
  user_name             = sa.Column(sa.ForeignKey("user.user_name"),      nullable=False)
  comment_content       = sa.Column(sa.String,                            nullable=False)
  comment_timestamp     = sa.Column(sa.Integer,                           nullable=False)
  # For sub-comment
  parent_comment_id     = sa.Column(sa.ForeignKey("comment.comment_id"),  nullable=True)
  to_user_id            = sa.Column(sa.ForeignKey("user.user_id"),        nullable=True)
  to_user_name          = sa.Column(sa.ForeignKey("user.user_name"),      nullable=True)

  @staticmethod
  def add_comment(comment: 'Comment'):
    ret = db.session.execute(
      sa.text(
        f"INSERT INTO {Comment.__table__.name} \
          (article_id, user_id, user_name, comment_content, comment_timestamp, parent_comment_id, to_user_id, to_user_name) \
          VALUES (:article_id, :user_id, :user_name, :comment_content, :comment_timestamp, :parent_comment_id, :to_user_id, :to_user_name) \
          RETURNING comment_id"
      ),
      {
        "article_id":                 comment.article_id, 
        "user_id":                    comment.user_id,
        "user_name":                  comment.user_name,
        "comment_content":            comment.comment_content, 
        "comment_timestamp":          comment.comment_timestamp,
        "parent_comment_id":          comment.parent_comment_id,
        "to_user_id":                 comment.to_user_id,
        "to_user_name":               comment.to_user_name
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
  def find_rangeof_comments_by_article_id(
    article_id,
    primary_comment_offset,
    primary_comment_count,
    sub_comment_count
  ):
    if primary_comment_count <= 0 or primary_comment_count is None:
      comments = db.session.execute(sa.select(Comment) \
        .where(sa.and_(Comment.article_id == article_id, Comment.parent_comment_id == None)) \
        .order_by(Comment.comment_timestamp.desc()) \
        .offset(primary_comment_offset)
      ).scalars()
    else:
      comments = db.session.execute(sa.select(Comment) \
        .where(sa.and_(Comment.article_id == article_id, Comment.parent_comment_id == None)) \
        .order_by(Comment.comment_timestamp.desc()) \
        .offset(primary_comment_offset) \
        .limit(primary_comment_count)
      ).scalars()
    comments = [comment for comment in comments]
    if comments:
      comment_ids = [str(comment.comment_id) for comment in comments]
      # Select sub-comment
      sub_comments = db.session.execute(
        sa.text(
          f"SELECT c.* FROM ( \
              SELECT \
                c1.*, \
                ( \
                  SELECT COUNT(*) + 1 FROM {Comment.__table__.name} AS c2 WHERE c1.parent_comment_id == c2.parent_comment_id AND c2.comment_timestamp < c1.comment_timestamp \
                ) AS rank \
              FROM {Comment.__table__.name} AS c1 WHERE c1.parent_comment_id IN {'(' + ','.join(comment_ids) +')'} AND c1.article_id == :article_id\
            ) AS c WHERE c.rank <= :sub_comment_count ORDER BY c.comment_timestamp"
        ),
        {
          "sub_comment_count": sub_comment_count,
          "article_id": article_id
        }
      )
      return True, comments, [sub_comment for sub_comment in sub_comments]
    else:
      return False, None, None

  @staticmethod
  def get_comments_count_by_article_id(article_id) -> int:
    count = db.session.execute(
      sa.select(sa.func.count().label("count")) \
      .where(sa.and_(Comment.article_id == article_id, Comment.parent_comment_id == None)) \
      .limit(1)
    ).first()
    return count["count"]

  @staticmethod
  def delete_comment_with_user_check(comment_id, user_id):
    result = db.session.execute(
      sa.delete(Comment) \
      .where(sa.and_(Comment.comment_id == comment_id, Comment.user_id == user_id)) \
    )
    db.session.commit()
    return result.rowcount