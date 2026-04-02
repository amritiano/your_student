from typing import List, Callable
from embeddings import embed_query, cosine_similarity


def retrieve_relevant_chunks(
    query: str,
    collection: dict,
    embed_fn: Callable = None,
    n_results: int = 4
) -> List[str]:
    if not collection or not collection.get("documents"):
        return []

    query_embedding = embed_query(query)
    documents = collection["documents"]
    embeddings = collection["embeddings"]

    scored = []
    for doc, emb in zip(documents, embeddings):
        score = cosine_similarity(query_embedding, emb)
        scored.append((score, doc))

    scored.sort(key=lambda x: x[0], reverse=True)
    return [doc for _, doc in scored[:n_results]]