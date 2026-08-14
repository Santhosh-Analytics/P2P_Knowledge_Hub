from p2p_knowledge_hub.exceptions.base import P2PHubException


class DocumentIDNotFoundError(P2PHubException):
    """Raises whenever the id is missing in the PSQL"""
