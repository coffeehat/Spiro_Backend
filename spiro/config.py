class _NetworkConfig:
  listen_ip = "0.0.0.0"
  port = "5000"
  token_key = ""

class _DbConfig:
  is_debug = True
  url = "sqlite:///comments.db"

class _EmailConfig:
  enabled = False
  smtp_server = ""
  port = 25
  password = ""
  send_addr = ""
  recv_addr = ""

class _MiscConfig:
  pass_salt = "spiro"

class SpiroConfig:
  website_name = "Sprio"
  website_domain = "localhost"
  is_https = False
  version = "v1.0"
  app_name = "spiro"
  network = _NetworkConfig
  db = _DbConfig
  email = _EmailConfig
  misc = _MiscConfig

def check_config():
  if not SpiroConfig.network.token_key:
    print("You Must Add a Config for Token Key")
    print("You Can Give Whatever String Value for that Token Key")
    print("But Need to Be SECRIT! PRIVATE!!!!")
    print("\n\n")
    print("------------------")
    print("Q: How to set Token Key?")
    print("A: Before you instantinate an `Server` object, you need to:")
    print("    from spiro import SpiroConfig")
    print("    SpiroConfig.network.token_key = WHATEVER KEY YOU WANT, BUT KEEP SECRIT!!!")
    raise RuntimeError