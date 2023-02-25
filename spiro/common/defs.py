import enum

class Role(enum.Enum):
  Admin = 0
  Member = 10
  Visitor = 100

class Defaults(enum.Enum):
  UserNameInactive = "Inactive"

class CommentListGetMethod(enum.Enum):
  COUNT_FROM_OFFSET = 0
  COUNT_FROM_COMMENT_ID = 1

class CommentDeleteType(enum.Enum):
  DELETE_UNDEFINED = 0
  DELETE_DIRECTLY = 1
  DELETE_BY_MARK = 2
  DELETE_DIRECTLY_WITH_PARENT = 3
