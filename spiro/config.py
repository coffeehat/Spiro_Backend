from easydict import EasyDict

config = EasyDict()
config.version = "v1.0"
config.app_name = "sprio"

# db
config.db = EasyDict()
config.db.is_debug = True

# email
config.email = EasyDict()
config.email.addr = ""
config.email.port = 25
config.email.smtp_server = ""
config.email.password = ""