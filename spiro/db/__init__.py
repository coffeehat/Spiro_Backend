from ..config import config

if config.db.is_debug:
  from .db_debug import get_comment
  from .db_debug import save_comment
  from .db_debug import get_comment_list
  from .db_debug import user_register
  from .db_debug import user_verify
  from .db_debug import user_login
  from .db_debug import verify_token
else:
  pass