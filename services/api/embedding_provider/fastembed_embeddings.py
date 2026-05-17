import numpy as np
from fastembed import TextEmbedding, SparseTextEmbedding

from services.api.config import config
from services.api.embedding_provider.base_embedding_provider import BaseEmbeddingProvider


class FastEmbedEmbeddingProvider(BaseEmbeddingProvider):
    def __init__(self):
        self._set_embedding_models()
        super().__init__()

    def _set_embedding_models(self) -> None:
        self.dense_embedding_model = TextEmbedding(config.fastembed.dense_model)
        self.sparse_embedding_model = SparseTextEmbedding(config.fastembed.sparse_model)

    def get_dense_embedding(self, document):
        return list(self.dense_embedding_model.embed([document]))[0]

    def get_sparse_embedding(self, document):
        return list(self.sparse_embedding_model.embed([document]))[0]


