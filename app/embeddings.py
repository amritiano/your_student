import numpy as np
from sentence_transformers import SentenceTransformer
from typing import List
import json
import os

EMBEDDING_MODEL = SentenceTransformer("all-MiniLM-L6-v2")

STORE = {
    "documents": [],
    "embeddings": []
}


def embed_texts(texts: List[str]) -> List[List[float]]:
    return EMBEDDING_MODEL.encode(texts).tolist()


def embed_query(query: str) -> List[float]:
    return EMBEDDING_MODEL.encode([query])[0].tolist()


def get_chroma_client(data_dir: str = None):
    return None


def get_or_create_collection(client=None, collection_name: str = "document_chunks"):
    return STORE


def embed_and_store(chunks: List[str], collection: dict):
    embeddings = embed_texts(chunks)
    collection["documents"] = chunks
    collection["embeddings"] = embeddings
    print("Stored " + str(len(chunks)) + " chunks in memory.")


def cosine_similarity(a: List[float], b: List[float]) -> float:
    a = np.array(a)
    b = np.array(b)
    if np.linalg.norm(a) == 0 or np.linalg.norm(b) == 0:
        return 0.0
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))