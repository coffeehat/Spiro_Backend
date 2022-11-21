from easydict import EasyDict

config = EasyDict()
config.version = "v1.0"
config.app_name = "sprio"

# db
config.db = EasyDict()
config.db.is_debug = True