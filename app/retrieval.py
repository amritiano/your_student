from typing import List, Callable


def retrieve_relevant_chunks(
    query: str,
    collection,
    embed_fn: Callable,
    n_results: int = 4
) -> List[str]:
    """
    Find the most relevant chunks for a query.

    embed_fn is passed in from main.py (no import needed here).
    This avoids the circular/broken import problem entirely.
    """
    query_embedding = embed_fn(query)
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=n_results
    )
    if results and results["documents"]:
        return results["documents"][0]
    return []