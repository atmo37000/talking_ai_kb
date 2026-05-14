import pytest
from ragas import EvaluationDataset, SingleTurnSample

from evaluator.ragas_evaluator import RagasEvaluator
from utils.clients_fabric import ClientsFabric


class TestRagasEvaluation:
    @pytest.fixture
    def golden_dataset(self):
        dataset = EvaluationDataset(samples=[
            SingleTurnSample(
                user_input="Какой инструмент используется для миграций базы данных?",
                response="Для миграций базы данных используется Alembic.",
                retrieved_contexts=["Alembic используется для управления миграциями базы данных в SQLAlchemy."]
            ),
            SingleTurnSample(
                user_input="Что такое FastAPI?",
                response="FastAPI — это современный Python-фреймворк для создания API.",
                retrieved_contexts=["FastAPI — это современный Python-фреймворк для создания API."]
            )
        ])

    def test_run_eval(self,dataset):
        db_client = ClientsFabric().create_db_client()
        llm = ClientsFabric().create_llm_client()
        # real unit tests will be added later
        RagasEvaluator(llm, db_client).start(dataset)
        assert True
