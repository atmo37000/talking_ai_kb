from abc import ABC, abstractmethod

from services.api.chunker.base_chunker import BaseChunker
from services.api.db_client.db_client import DbClient


class DataInjector(ABC):
    def __init__(self, db_client: DbClient, chunker: BaseChunker):
        pass

    @abstractmethod
    async def ingest_files(self):
        pass

