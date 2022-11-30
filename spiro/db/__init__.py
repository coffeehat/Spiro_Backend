from ..config import config

if config.db.is_debug:
  from .db_debug import get_comment
  from .db_debug import save_comment
  from .db_debug import get_comment_list
  from .db_debug import user_register
  from .db_debug import user_verify
else:
  pass