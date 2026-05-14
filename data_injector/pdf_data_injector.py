import os
from datetime import datetime
from pathlib import Path

from langchain_community.document_loaders import PDFPlumberLoader
from langchain_core.documents import Document
from qdrant_client.http.models import PointStruct, SparseVector

from chunker.base_chunker import BaseChunker
from data_injector.data_injector import DataInjector
from db_client.db_client import DbClient
from config import config


class PdfDataInjector(DataInjector):
    def __init__(self, db_client: DbClient, chunker: BaseChunker):
        self.db_client = db_client
        self.chunker = chunker
        self.base_path = Path(config.docs_path)
        super().__init__(db_client, chunker)

    def _get_pdf_files_paths(self) -> list[str]:
        if not os.path.exists(self.base_path):
            raise ValueError(f'No such path {self.base_path}')

        file_paths = [os.path.join(self.base_path, f) for f in os.listdir(self.base_path) if f.endswith(".pdf")]

        if len(file_paths) == 0:
            raise ValueError(f'No files in {self.base_path}')

        return file_paths

    def _load_file(self, doc_path: str) -> Document:
        loader = PDFPlumberLoader(doc_path)
        return loader.load()

    async def ingest_files(self) -> None:
        for doc_path in self._get_pdf_files_paths():
            doc = self._load_file(doc_path)
            chunks = self.chunker.split_to_chunks(doc)
            points = []
            for i, ch in enumerate(chunks):
                dense_embedding = self.db_client.embedding_provider.get_dense_embedding(ch.page_content)
                sparse_embedding = self.db_client.embedding_provider.get_sparse_embedding(ch.page_content)
                points.append(
                    PointStruct(
                        id=i,
                        vector={
                            "dense": dense_embedding.tolist(),
                            "sparse": SparseVector(
                                indices=sparse_embedding.indices.tolist(),
                                values=sparse_embedding.values.tolist()
                            )
                        },
                        payload={"text": ch}
                    )
                )

            await self.db_client.upsert(config.qdrant.collection_name, points)