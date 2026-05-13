from abc import ABC, abstractmethod

from db_client.db_client import DbClient


class DataInjector(ABC):
    def __init__(self, db_client: DbClient):
        pass

    @abstractmethod
    async def ingest_files(self):
        pass

