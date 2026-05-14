from chunker.base_chunker import BaseChunker
from langchain_core.documents import Document
from typing import List


class MarkdownChunker(BaseChunker):
    def __init__(self):
        super().__init__()

    def split_to_chunks(self, doc: Document) -> List[Document]:
        from langchain_text_splitters import MarkdownTextSplitter

        splitter = MarkdownTextSplitter(chunk_size=400, chunk_overlap=100)
        chunks = splitter.create_documents([doc.page_content])

        return chunks

