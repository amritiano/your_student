import chromadb
from sentence_transformers import SentenceTransformer
from typing import List

# Load once, reuse everywhere
EMBEDDING_MODEL = SentenceTransformer("all-MiniLM-L6-v2")


def embed_texts(texts: List[str]) -> List[List[float]]:
    """Convert a list of strings into embedding vectors."""
    return EMBEDDING_MODEL.encode(texts).tolist()


def embed_query(query: str) -> List[float]:
    """Convert a single query string into an embedding vector."""
    return EMBEDDING_MODEL.encode([query])[0].tolist()


def get_chroma_client(data_dir: str):
    """Create a persistent ChromaDB client at the given folder."""
    return chromadb.PersistentClient(path=data_dir)


def get_or_create_collection(client, collection_name: str = "document_chunks"):
    """Get or create a ChromaDB collection."""
    return client.get_or_create_collection(name=collection_name)


def embed_and_store(chunks: List[str], collection):
    """Embed each chunk and store in ChromaDB."""
    embeddings = embed_texts(chunks)
    ids = ["chunk_" + str(i) for i in range(len(chunks))]
    collection.upsert(documents=chunks, embeddings=embeddings, ids=ids)
    print("Stored " + str(len(chunks)) + " chunks in ChromaDB.")