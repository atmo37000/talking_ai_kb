from elasticsearch import Elasticsearch

from services.api.config import config
from services.api.utils.logger import get_logger

logger = get_logger()


class ElasticClient:
    def __init__(self):
        self.es = Elasticsearch(config.elastic_host)

    def create_index(self, index_name):
        self.es.indices.create(index=index_name)

    def is_index_exist(self, index_name):
        return self.es.indices.exists(index=index_name)

    def health(self):
        if self.es.ping():
            logger.info("Подключено к Elasticsearch!")
        else:
            logger.info("Не удалось подключиться.")

    def add(self, index_name, doc):
        response = self.es.index(index=index_name, document=doc)
        self.es.indices.refresh(index=index_name)

    def query(self, query, index_name):
        search_res = self.es.search(index=index_name, query=query)

        print(f"Найдено документов: {search_res['hits']['total']['value']}")
        for hit in search_res['hits']['hits']:
            print(f"ID: {hit['_id']}, Source: {hit['_source']}")

    def update(self, index_name, doc_id, doc):
        self.es.update(index=index_name, id=doc_id, doc=doc)
