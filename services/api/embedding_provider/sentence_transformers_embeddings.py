from services.api.config import config
from services.api.embedding_provider.base_embedding_provider import BaseEmbeddingProvider


class SentenceTransformerEmbeddingProvider(BaseEmbeddingProvider):
    def _set_embedding_models(self):
        from sentence_transformers import SentenceTransformer
        from sentence_transformers import SparseEncoder

        self.dense_embedding_model = SentenceTransformer(config.dense_embedding_model)
        self.sparse_embedding_model = SparseEncoder(config.sparse_embedding_model)

    def get_dense_embeddings(self, document):
        return self.dense_embedding_model.encode(document)

    def get_sparse_embeddings(self, document):
        return self.sparse_embedding_model.encode(document)

