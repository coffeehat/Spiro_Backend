import typing
import sqlalchemy as sa

from ..db import db

class Comment(db.Model):
  comment_id            = sa.Column(sa.Integer,                             primary_key=True)
  article_uuid          = sa.Column(sa.ForeignKey("article.article_uuid"),  nullable=False)
  user_id               = sa.Column(sa.ForeignKey("user.user_id"),          nullable=False)
  user_name             = sa.Column(sa.ForeignKey("user.user_name"),        nullable=False)
  comment_content       = sa.Column(sa.String,                              nullable=False)
  comment_timestamp     = sa.Column(sa.Integer,                             nullable=False)
  # For sub-comment
  parent_comment_id     = sa.Column(sa.ForeignKey("comment.comment_id"),    nullable=True)
  to_user_id            = sa.Column(sa.ForeignKey("user.user_id"),          nullable=True)
  to_user_name          = sa.Column(sa.ForeignKey("user.user_name"),        nullable=True)

  @staticmethod
  def add_comment(comment: 'Comment'):
    ret = db.session.execute(
      sa.text(
        f"INSERT INTO {Comment.__table__.name} \
          (article_uuid, user_id, user_name, comment_content, comment_timestamp, parent_comment_id, to_user_id, to_user_name) \
          VALUES (:article_uuid, :user_id, :user_name, :comment_content, :comment_timestamp, :parent_comment_id, :to_user_id, :to_user_name) \
          RETURNING comment_id"
      ),
      {
        "article_uuid":               comment.article_uuid, 
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
  def find_rangeof_comments_by_offset_and_article_uuid(
    article_uuid,
    primary_start_comment_offset,
    primary_comment_count,
    sub_comment_count
  ):
    if primary_comment_count <= 0 or primary_comment_count is None:
      # TODO: Do we really need this?
      comments = db.session.execute(sa.select(Comment) \
        .where(sa.and_(Comment.article_uuid == article_uuid, Comment.parent_comment_id == None)) \
        .order_by(Comment.comment_timestamp.desc()) \
        .offset(primary_start_comment_offset)
      ).scalars()
    else:
      comments = db.session.execute(sa.select(Comment) \
        .where(sa.and_(Comment.article_uuid == article_uuid, Comment.parent_comment_id == None)) \
        .order_by(Comment.comment_timestamp.desc()) \
        .offset(primary_start_comment_offset) \
        .limit(primary_comment_count)
      ).scalars()
    comments = [comment for comment in comments]
    if comments:
      # Select sub-comment
      sub_comments = Comment._find_sub_comments_by_primary_comments_and_article_uuid(
        article_uuid,
        comments,
        sub_comment_count
      )
      return True, comments, sub_comments
    else:
      return False, None, None

  @staticmethod
  def find_rangeof_comments_by_comment_id_and_article_uuid(
    article_uuid,
    primary_start_comment_id,
    primary_comment_count,
    sub_comment_count,
    is_newer
  ):
    if is_newer:
      textual_sql = sa.text(
        f"select * from {Comment.__table__.name} where comment_id > :primary_start_comment_id and article_uuid == :article_uuid and parent_comment_id is null\
          union \
          select * from {Comment.__table__.name} where \
            comment_id == ( \
              select max(comment_id) from comment where comment_id < :primary_start_comment_id and article_uuid == :article_uuid and parent_comment_id is null\
            ) order by comment_id asc limit :primary_comment_count"
      ).bindparams(
        primary_start_comment_id = primary_start_comment_id,
        primary_comment_count = primary_comment_count,
        article_uuid = article_uuid
      )
      orm_sql = sa.select(Comment).from_statement(textual_sql)
      comments = db.session.execute(orm_sql).scalars()
      # We can also use below statement to get comments
      # s1 = sa.select(Comment).where(sa.and_(Comment.comment_id > primary_start_comment_id, Comment.article_uuid == :article_uuid, Comment.parent_comment_id == None))
      # s2 = sa.select(Comment).where(Comment.comment_id == sa.select(sa.func.max(Comment.comment_id)).where(sa.and_(Comment.comment_id < primary_start_comment_id, Comment.article_uuid == :article_uuid, Comment.parent_comment_id == None)))
      # q  = sa.select(Comment).from_statement(s1.union(s2).order_by(Comment.comment_id.asc()).limit(primary_comment_count))
      # comments = db.session.execute(q).scalars()

      # comment id from small to big (from old to new)
      # so we need a reverse to make it from new to old
      comments = [comment for comment in comments]
      comments.reverse()
    else:
      textual_sql = sa.text(
        f"select * from {Comment.__table__.name} where comment_id < :primary_start_comment_id and article_uuid == :article_uuid and parent_comment_id is null \
          union \
          select * from {Comment.__table__.name} where \
            comment_id == ( \
              select min(comment_id) from comment where comment_id > :primary_start_comment_id and article_uuid == :article_uuid and parent_comment_id is null \
            ) order by comment_id desc limit :primary_comment_count"
      ).bindparams(
        primary_start_comment_id = primary_start_comment_id,
        primary_comment_count = primary_comment_count,
        article_uuid = article_uuid
      )
      orm_sql = sa.select(Comment).from_statement(textual_sql)
      comments = db.session.execute(orm_sql).scalars()

      # comment id from big to small (from new to old)
      comments = [comment for comment in comments]

    if comments:
      # Select sub-comment
      sub_comments = Comment._find_sub_comments_by_primary_comments_and_article_uuid(
        article_uuid,
        comments,
        sub_comment_count
      )
      return True, comments, sub_comments
    else:
      return False, None, None

  @staticmethod
  def find_rangeof_comments_bilateral_by_comment_id_and_article_uuid(
    article_uuid,
    primary_start_comment_id,
    primary_single_side_comment_count,
    sub_comment_count
  ):
    textual_sql = sa.text(
      f"select * from \
          (select * from {Comment.__table__.name} \
            where parent_comment_id is null \
              and comment_id <= :primary_start_comment_id \
              and article_uuid == :article_uuid \
            order by comment_id desc limit :primary_single_side_comment_count) \
        union \
        select * from \
          (select * from {Comment.__table__.name} \
            where parent_comment_id is null \
              and comment_id >= :primary_start_comment_id \
              and article_uuid == :article_uuid \
            order by comment_id asc limit :primary_single_side_comment_count) \
        order by comment_id desc"
    ).bindparams(
      primary_start_comment_id = primary_start_comment_id,
      primary_single_side_comment_count = primary_single_side_comment_count + 1,
      article_uuid = article_uuid
    )
    orm_sql = sa.select(Comment).from_statement(textual_sql)
    comments = db.session.execute(orm_sql).scalars()
    comments = [comment for comment in comments]

    if comments and \
      next((comment for comment in comments if comment.comment_id == primary_start_comment_id), None):
      sub_comments = Comment._find_sub_comments_by_primary_comments_and_article_uuid(
        article_uuid,
        comments,
        sub_comment_count
      )
      return True, comments, sub_comments
    else:
      return False, None, None

  @staticmethod
  def find_rangeof_sub_comments_bilateral_by_comment_id_and_article_uuid(
    article_uuid,
    sub_start_comment_id,
    sub_single_side_comment_count
  ):
    textual_sql = sa.text(
      f"select * from \
          (select * from {Comment.__table__.name} \
            where parent_comment_id == ( \
                select parent_comment_id from {Comment.__table__.name} where comment_id == :sub_start_comment_id) \
              and comment_id <= :sub_start_comment_id \
              and article_uuid == :article_uuid \
            order by comment_id desc limit :sub_single_side_comment_count) \
        union \
        select * from \
          (select * from {Comment.__table__.name} \
            where parent_comment_id == ( \
                select parent_comment_id from {Comment.__table__.name} where comment_id == :sub_start_comment_id) \
              and comment_id >= :sub_start_comment_id \
              and article_uuid == :article_uuid \
            order by comment_id asc limit :sub_single_side_comment_count) \
        order by comment_id desc"
    ).bindparams(
      sub_start_comment_id = sub_start_comment_id,
      sub_single_side_comment_count = sub_single_side_comment_count + 1,
      article_uuid = article_uuid
    )
    orm_sql = sa.select(Comment).from_statement(textual_sql)
    sub_comments = db.session.execute(orm_sql).scalars()
    sub_comments = [comment for comment in sub_comments]

    if sub_comments:
      return True, sub_comments
    else:
      return False, None

  @staticmethod
  def _find_sub_comments_by_primary_comments_and_article_uuid(
    article_uuid,
    primary_comments,
    sub_comment_count
  ):
    comment_ids = [str(comment.comment_id) for comment in primary_comments]
    # Select sub-comment
    textual_sql = sa.text(
      f"SELECT c.* FROM ( \
          SELECT \
            c1.*, \
            ( \
              SELECT COUNT(*) + 1 FROM {Comment.__table__.name} AS c2 WHERE c1.parent_comment_id == c2.parent_comment_id AND c2.comment_timestamp < c1.comment_timestamp \
            ) AS rank \
          FROM {Comment.__table__.name} AS c1 WHERE c1.parent_comment_id IN {'(' + ','.join(comment_ids) +')'} AND c1.article_uuid == :article_uuid\
        ) AS c WHERE c.rank <= :sub_comment_count ORDER BY c.comment_timestamp"
    ).bindparams(
      sub_comment_count = sub_comment_count,
      article_uuid = article_uuid
    )
    orm_sql = sa.select(Comment).from_statement(textual_sql)
    sub_comments = db.session.execute(orm_sql).scalars()
    return [sub_comment for sub_comment in sub_comments]

  @staticmethod
  def find_rangeof_sub_comments_by_parent_comment_id(
    parent_comment_id,
    sub_start_comment_offset,
    sub_comment_count
  ):
    if sub_comment_count <= 0 or sub_comment_count is None:
      sub_comments = db.session.execute(sa.select(Comment) \
        .where(Comment.parent_comment_id == parent_comment_id) \
        .order_by(Comment.comment_timestamp.asc()) \
        .offset(sub_start_comment_offset)
      ).scalars()
    else:
      sub_comments = db.session.execute(sa.select(Comment) \
        .where(Comment.parent_comment_id == parent_comment_id) \
        .order_by(Comment.comment_timestamp.asc()) \
        .offset(sub_start_comment_offset) \
        .limit(sub_comment_count)
      ).scalars()
    
    if sub_comments:
      return True, [sub_comment for sub_comment in sub_comments]
    else:
      return False, None

  @staticmethod
  def find_rangeof_sub_comments_by_comment_id_and_article_uuid(
    article_uuid,
    parent_comment_id,
    sub_start_comment_id,
    sub_comment_count,
    is_newer
  ):
    if is_newer:
      textual_sql = sa.text(
        f"select * from {Comment.__table__.name} where comment_id > :sub_start_comment_id and article_uuid == :article_uuid and parent_comment_id == :parent_comment_id \
          union \
          select * from {Comment.__table__.name} where \
            comment_id == ( \
              select max(comment_id) from comment where comment_id < :sub_start_comment_id and article_uuid == :article_uuid and parent_comment_id == :parent_comment_id\
            ) order by comment_id asc limit :sub_comment_count"
      ).bindparams(
        sub_start_comment_id = sub_start_comment_id,
        sub_comment_count = sub_comment_count,
        article_uuid = article_uuid,
        parent_comment_id = parent_comment_id
      )
      orm_sql = sa.select(Comment).from_statement(textual_sql)
      sub_comments = db.session.execute(orm_sql).scalars()

      # comment id from small to big (from old to new)
      # so we need a reverse to make it from new to old
      sub_comments = [sub_comment for sub_comment in sub_comments]
      sub_comments.reverse()
    else:
      textual_sql = sa.text(
        f"select * from {Comment.__table__.name} where comment_id < :sub_start_comment_id and article_uuid == :article_uuid and parent_comment_id == :parent_comment_id \
          union \
          select * from {Comment.__table__.name} where \
            comment_id == ( \
              select min(comment_id) from comment where comment_id > :sub_start_comment_id and article_uuid == :article_uuid and parent_comment_id == :parent_comment_id \
            ) order by comment_id desc limit :sub_comment_count"
      ).bindparams(
        sub_start_comment_id = sub_start_comment_id,
        sub_comment_count = sub_comment_count,
        article_uuid = article_uuid,
        parent_comment_id = parent_comment_id
      )
      orm_sql = sa.select(Comment).from_statement(textual_sql)
      sub_comments = db.session.execute(orm_sql).scalars()

      # comment id from big to small (from new to old)
      sub_comments = [sub_comment for sub_comment in sub_comments]
    
    if sub_comments:
      return True, sub_comments
    else:
      return False, None

  @staticmethod
  def get_comments_count_by_article_uuid(article_uuid) -> int:
    count = db.session.execute(
      sa.select(sa.func.count()) \
      .where(sa.and_(Comment.article_uuid == article_uuid, Comment.parent_comment_id == None)) \
      .limit(1)
    ).scalars().first()
    return count

  @staticmethod
  def delete_comment_with_user_check(comment_id, user_id):
    result = db.session.execute(
      sa.delete(Comment) \
      .where(sa.and_(Comment.comment_id == comment_id, Comment.user_id == user_id)) \
    )
    db.session.commit()
    return result.rowcount