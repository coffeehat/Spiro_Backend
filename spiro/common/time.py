import datetime
import time
from email import utils

def get_current_time():
  return datetime.datetime.now()

def get_time_stamp():
  return get_current_time().timestamp()