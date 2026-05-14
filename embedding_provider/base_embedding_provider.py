from abc import ABC, abstractmethod

import numpy as np
from fastembed import SparseEmbedding


class BaseEmbeddingProvider(ABC):
    def __init__(self):
        pass

    @abstractmethod
    def _set_embedding_models(self):
        pass

    @abstractmethod
    def get_dense_embedding(self, document: str) -> np.ndarray:
        pass

    @abstractmethod
    def get_sparse_embedding(self, document: str) -> SparseEmbedding:
        pass