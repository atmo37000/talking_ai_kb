from typing import List

from langchain_core.documents import Document

from services.api.chunker.base_chunker import BaseChunker


class PdfChunker(BaseChunker):
    def __init__(self):
        super().__init__()

    def split_to_chunks(self, doc: Document) -> List[Document]:
        from langchain_text_splitters import RecursiveCharacterTextSplitter

        splitter = RecursiveCharacterTextSplitter(
            chunk_size=400, chunk_overlap=100
        )

        chunks = splitter.create_documents([doc.page_content])

        return chunks

