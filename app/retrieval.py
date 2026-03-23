# app/retrieval.py
from embeddings import embed_query

def retrieve_relevant_chunks(query: str, collection, n_results: int = 4) -> List[str]:
    """
    Find the top-N most semantically similar chunks to the query.
    This is the core of RAG — grounding the AI in actual document content.
    """
    query_embedding = embed_query(query)
    
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=n_results
    )
    
    # results["documents"] is a list of lists, so flatten
    return results["documents"][0] if results["documents"] else []