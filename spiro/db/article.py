import typing
import sqlalchemy as sa

from ..db import db

class Article(db.Model):
  article_id            = sa.Column(sa.Integer,           primary_key=True)
  article_uuid          = sa.Column(sa.String,            nullable=False, unique=True)
  article_link          = sa.Column(sa.String)
  article_name          = sa.Column(sa.String)
  article_read_count    = sa.Column(sa.Integer,           nullable=False)

  @staticmethod
  def get_article_read_count_by_uuid(article_uuid) -> typing.Tuple[bool, typing.Optional[int]]:
    count = db.session.execute(sa.select(Article.article_read_count) \
      .where(Article.article_uuid == article_uuid) \
      .limit(1)
    ).scalars().first()
    if count:
      return True, count,
    else:
      return False, None

  @staticmethod
  def incre_article_read_count_by_uuid(article_uuid) -> typing.Tuple[bool, typing.Optional['Article']]:
    ret = db.session.execute(
      sa.text(
        f"UPDATE {Article.__table__.name} \
          SET article_read_count = article_read_count + 1\
          WHERE article_uuid == :article_uuid \
          RETURNING *"
      ),
      {
        "article_uuid": article_uuid
      }
    ).first()
    db.session.commit()
    return ret

  @staticmethod
  def add_article(article) -> None:
    db.session.add(article)
    db.session.commit()

  @staticmethod
  def update_article_name_by_uuid(article_uuid, article_name):
    db.session.execute(
      sa.update(Article.article_name) \
      .values(article_name) \
      .where(Article.article_uuid == article_uuid) \
    )
    db.session.commit()

  @staticmethod
  def update_article(article):
    db.session.execute(
      sa.update(Article) \
      .values(article) \
      .where(Article.article_uuid == article.article_uuid) \
    )
    db.session.commit()