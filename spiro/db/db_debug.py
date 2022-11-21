import uuid

from ..common.exceptions import handle_exception, DbNotFound, ArgInvalid
from ..common.time import get_current_time

db_comment = {}

@handle_exception
def get_comment_list(article_id, range_start = 0, range_end = -1):
  if range_start < 0:
    raise ArgInvalid("Range_start is less than 0")
  
  if range_end != -1 and range_end <= range_start:
    raise ArgInvalid("Range_end should be greater than Range_end, at least one")
  
  if article_id in db_comment:
    if range_end == -1 or range_end > len(db_comment[article_id]):
      return {
        "article_id": article_id,
        "comment_list": db_comment[article_id][range_start:]
      }
    elif range_end > 0 and range_end <= len(db_comment[article_id]):
      return {
        "article_id": article_id,
        "comment_list": db_comment[article_id][range_start:range_end]
      }
    else:
      raise ArgInvalid("Range_end invalid")
  else:
    raise DbNotFound("Article_id does not exist in backend")

@handle_exception
def get_comment(comment_id):
  for article_id in db_comment:
    for item in db_comment[article_id]:
      if item["comment_id"] == comment_id:
        return item
  raise DbNotFound("Comment_id does not exist in backend")

@handle_exception
def save_comment(article_id, comment):
  if not article_id in db_comment:
    db_comment[article_id] = []

  item = {
    "article_id":   article_id,
    "comment_id":   int(uuid.uuid4().hex, 16),
    "comment_time": get_current_time(),
    "comment":      comment
  }

  db_comment[article_id].append(item)
  return item