from p2p_knowledge_hub.exceptions.base import P2PHubException


class DBSessionError(P2PHubException):
    """Raises whenever there is an issue with the sessison"""


class DBConstraintError(P2PHubException):
    """Raises whenever we met db constraint violations"""


class DBNotnullError(P2PHubException):
    """Raises whenever we met db constraint violations"""


class DBUnknownError(P2PHubException):
    """Raises whenever we met db constraint violations"""


class DBSyntexError(P2PHubException):
    """Raises whenever we met db constraint violations"""


class DBConnectionError(P2PHubException):
    """Raises whenever the script failed to reach database"""


class DBNotFoundError(P2PHubException):
    """Raised when a requested record (e.g. by ID) does not exist in the database"""
