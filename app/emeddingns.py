# app/embeddings.py
import chromadb
from sentence_transformers import SentenceTransformer
from typing import List

# Load a lightweight, fast embedding model
EMBEDDING_MODEL = SentenceTransformer("all-MiniLM-L6-v2")

def get_chroma_client():
    """Create a persistent ChromaDB client."""
    return chromadb.PersistentClient(path="./data/chroma_db")

def get_or_create_collection(client, collection_name: str = "document_chunks"):
    return client.get_or_create_collection(name=collection_name)

def embed_and_store(chunks: List[str], collection):
    """
    Embed each chunk and store in ChromaDB.
    Each chunk gets a unique ID and its embedding vector.
    """
    embeddings = EMBEDDING_MODEL.encode(chunks).tolist()
    ids = [f"chunk_{i}" for i in range(len(chunks))]
    
    collection.upsert(
        documents=chunks,
        embeddings=embeddings,
        ids=ids
    )
    print(f"✅ Stored {len(chunks)} chunks in ChromaDB.")

def embed_query(query: str) -> List[float]:
    """Convert a query string into an embedding vector."""
    return EMBEDDING_MODEL.encode([query])[0].tolist()