from p2p_knowledge_hub.reranker.base_reranker import BaseReranker


class CrossEncoderReranker(BaseReranker):
    def __init__(self, model_name: str) -> None:
        self.model_name = model_name
