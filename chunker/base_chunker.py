from abc import ABC
from typing import List

from langchain_core.documents import Document


class BaseChunker(ABC):
    def __init__(self):
        pass

    def split_to_chunks(self, doc: Document) -> List[Document]:
        pass