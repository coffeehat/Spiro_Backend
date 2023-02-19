from .email import get_email_worker
from .utils import gen_random_string
from ..config import SpiroConfig
from ..common.exceptions import *
from ..common.lock import w_lock
from ..db.user import User

# veri_id -> user_id
verify_queue = {}
# user_id -> veri_id
verify_queue_reverse = {}

def _gen_verification_link(veri_id):
  return f"{'https' if SpiroConfig.is_https else 'http'}://{SpiroConfig.website_domain}:{SpiroConfig.network.port}/{SpiroConfig.version}/email_verify/{veri_id}"

def _gen_verification_id():
  while True:
    veri_id = gen_random_string(32)
    if not veri_id in verify_queue:
      return veri_id

def send_mail_verification(user_id, user_name, user_email):
  if not user_id in verify_queue_reverse:
    veri_id = _gen_verification_id()
    veri_link = _gen_verification_link(veri_id)
    verify_queue[veri_id] = user_id
    verify_queue_reverse[user_id] = veri_id
  else:
    veri_id = verify_queue_reverse[user_id]
    veri_link = _gen_verification_link(veri_id)
  get_email_worker().send_email_verify(user_email, user_name, veri_link)

def handle_verification(veri_id):
  if not veri_id in verify_queue:
    raise UserException
  else:
    _handle_verification(veri_id)

@w_lock
def _handle_verification(veri_id):
  user_id = verify_queue[veri_id]
  User.update_user_email_verification(user_id, True)
  del verify_queue[veri_id]
  del verify_queue_reverse[user_id]