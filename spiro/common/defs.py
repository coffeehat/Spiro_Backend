import enum

class Role(enum.Enum):
  Admin = 0
  Member = 10
  Visitor = 100

class Defaults(enum.Enum):
  UserNameInactive = "Inactive"