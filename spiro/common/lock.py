from readerwriterlock import rwlock

global_rw_lock = rwlock.RWLockWriteD()

def r_lock(func):
  def wrapper(*args, **kwargs):
    with global_rw_lock.gen_rlock():
      return func(*args, **kwargs)
  return wrapper

def w_lock(func):
  def wrapper(*args, **kwargs):
    with global_rw_lock.gen_wlock():
      return func(*args, **kwargs)
  return wrapper