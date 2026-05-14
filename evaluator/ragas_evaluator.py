import asyncio

from pydantic import BaseModel
from ragas.dataset_schema import SingleTurnSample
from ragas.metrics.collections import Faithfulness, AnswerRelevancy, ContextRelevance

from db_client.db_client import DbClient
from llm_client.base_llm_client import BaseLLMClient


class Result(BaseModel):
    faithfulness: float
    answer_relevancy: float
    context_relevance: float


class RagasEvaluator:
    def __init__(self, llm_client: BaseLLMClient, db_client: DbClient):
        self.llm_client = llm_client
        self.db_client = db_client

    async def evaluate_sample(self, sample: SingleTurnSample) -> Result:
        faith = await Faithfulness(llm=self.llm_client.llm).ascore(
            user_input=sample.user_input,
            response=sample.response,
            retrieved_contexts=sample.retrieved_contexts
        )
        ar = await AnswerRelevancy(llm=self.llm_client.llm, embeddings=self.db_client.embedding_model).ascore(
            user_input=sample.user_input,
            response=sample.response
        )
        cr = await ContextRelevance(llm=self.llm_client.llm, embeddings=self.db_client.embedding_model).ascore(
            user_input=sample.user_input,
            retrieved_contexts=sample.retrieved_contexts
        )
        return Result(
            faithfulness=faith.value,
            answer_relevancy=ar.value,
            context_relevance=cr.value
        )


    async def start(self, dataset):
        tasks = [self.evaluate_sample(sample) for sample in dataset.samples]
        results = await asyncio.gather(*tasks)
        for i, res in enumerate(results):
            print(f"Sample {i+1}: {res}")
