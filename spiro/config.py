from easydict import EasyDict

config = EasyDict()
config.version = "v1.0"
config.app_name = "sprio"

# network
config.network = EasyDict()
config.network.listen_ip = "0.0.0.0"
config.network.port = "5000"

# db
config.db = EasyDict()
config.db.is_debug = True

# email
config.email = EasyDict()
config.email.enabled = False
config.email.addr = ""
config.email.port = 25
config.email.smtp_server = ""
config.email.password = ""