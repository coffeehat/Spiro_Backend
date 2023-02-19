class _NetworkConfig:
  listen_ip = "0.0.0.0"
  port = "5000"

class _DbConfig:
  is_debug = True
  url = "sqlite:///comments.db"

class _EmailConfig:
  enabled = False
  smtp_server = ""
  port = 25
  password = ""
  send_addr = ""

class _MiscConfig:
  pass_salt = "spiro"

class SpiroConfig:
  version = "v1.0"
  app_name = "spiro"
  network = _NetworkConfig
  db = _DbConfig
  email = _EmailConfig
  misc = _MiscConfig
