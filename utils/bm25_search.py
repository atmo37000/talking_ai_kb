import numpy as np
from rank_bm25 import BM25Okapi


class BM25Search:
    def __init__(self):
        pass

    def get_results(self, query, documents):
        tokenized_docs = [doc.lower().split() for doc in documents]
        bm25 = BM25Okapi(tokenized_docs)
        tokenized_query = query.lower().split()
        bm25_scores = bm25.get_scores(tokenized_query)
        best_doc_id = np.argmax(bm25_scores)
        return documents[best_doc_id]


