from p2p_knowledge_hub.exceptions.base import P2PHubException


class NoChunksProducedError(P2PHubException):
    """Raises when a document does not produce any chunks"""
