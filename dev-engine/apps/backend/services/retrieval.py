from qdrant_client import QdrantClient
from ..core.config import settings

async def get_embedding(query: str):
    raise NotImplementedError

async def retrieve_context(query: str, limit: int = 8):
    client = QdrantClient(url=settings.QDRANT_URL)
    vector = await get_embedding(query)  # from embeddings.py
    results = client.search(
        collection_name="repo_files",
        query_vector=vector,
        limit=limit
    )
    return [hit.payload for hit in results]