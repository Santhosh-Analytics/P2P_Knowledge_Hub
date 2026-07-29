from p2p_knowledge_hub.exceptions.base import P2PHubException


class P2PIngessionError(P2PHubException):
    """Raises Exceptions happening in the Ingesion service"""


class DuplicateDocumentError(P2PIngessionError):
    """Raises whenerver we receive a exact duplicate docuemnt during
    ingestion."""
