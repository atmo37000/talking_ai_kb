from utils.bm25_search import BM25Search


def test_get_results():
    documents = [
        "Python - высокоуровневый язык программирования.",
        "RAG использует векторные базы данных для поиска контекста.",
        "Гибридный поиск объединяет семантический поиск и BM25.",
        "FAISS - библиотека для быстрого поиска ближайших соседей.",
        "LLM (Large Language Models) генерируют текст."
    ]

    query = "Как работает гибридный поиск в RAG?"

    res = BM25Search().get_results(query, documents)
    print(res)
    assert True