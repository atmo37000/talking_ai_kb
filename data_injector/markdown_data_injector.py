import os
from datetime import datetime
from pathlib import Path

from qdrant_client.http.models import PointStruct

from data_injector.data_injector import DataInjector
from db_client.db_client import DbClient
from utils.config import config
from langchain_core.document_loaders import BaseLoader
from langchain_core.documents import Document


class MyCustomLoader(BaseLoader):
    def __init__(self, file_path):
        self.file_path = file_path
    def load(self):
        with open(self.file_path, "r", encoding="utf-8") as f:
            text = f.read()
        metadata = {"source": self.file_path}
        return [Document(page_content=text, metadata=metadata)]


class MarkdownDataInjector(DataInjector):
    def __init__(self, db_client: DbClient):
        self.db_client = db_client
        self.base_path = Path(config.docs_path)
        super().__init__()

    def _get_markdown_files_paths(self) -> list[str]:
        if not os.path.exists(self.base_path):
            raise ValueError(f'No such path {self.base_path}')

        file_paths = [os.path.join(self.base_path, f) for f in os.listdir(self.base_path) if f.endswith(".md")]

        if len(file_paths) == 0:
            raise ValueError(f'No files in {self.base_path}')

        return file_paths

    def _load_file(self, doc_path):
        loader = MyCustomLoader(doc_path)
        return loader.load()


    def _split_doc_to_chunks(self, lang_doc):
        from langchain_text_splitters import MarkdownTextSplitter

        splitter = MarkdownTextSplitter(chunk_size=400, chunk_overlap=100)
        chunks = splitter.split_documents(lang_doc)

        return chunks

    async def ingest_md_files(self, dir_name: str) -> None:
        for doc_path in self._get_markdown_files_paths():
            lang_doc = self._load_file(doc_path)
            chunks = self._split_doc_to_chunks(lang_doc)
            embeddings = [self.db_client.embedding_model.encode(ch.page_content) for ch in chunks]
            points = [
                PointStruct(id=i, vector=emb.tolist(), payload={'text': ch, 'doc_path': doc_path, 'updated_at': datetime.now()})
                for i, (ch, emb) in enumerate(zip(chunks, embeddings))
            ]
            await self.db_client.upsert(config.qdrant.collection_name, points)