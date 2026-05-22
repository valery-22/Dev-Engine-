import asyncio
import git
from pathlib import Path
import uuid
from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams, PointStruct
from ..utils.embeddings import get_embedding
from ..utils.logger import logger
from ..core.config import settings

async def ingest_repository(repo_url: str):
    repo_name = repo_url.split("/")[-1].replace(".git", "")
    local_path = Path(f"/tmp/repos/{repo_name}")
    local_path.parent.mkdir(parents=True, exist_ok=True)

    if local_path.exists():
        git.Repo(local_path).remotes.origin.pull()
    else:
        git.Repo.clone_from(repo_url, str(local_path), env={"GIT_ASKPASS": "echo", "GIT_USERNAME": "x-access-token", "GIT_PASSWORD": settings.GITHUB_TOKEN})

    client = QdrantClient(url=settings.QDRANT_URL)
    collection_name = "repo_files"

    if not client.collection_exists(collection_name):
        client.create_collection(
            collection_name=collection_name,
            vectors_config=VectorParams(size=1536, distance=Distance.COSINE)
        )

    for py_file in local_path.rglob("*.py"):
        try:
            content = py_file.read_text(encoding="utf-8")
            vector = await get_embedding(content[:8000])
            client.upsert(
                collection_name=collection_name,
                points=[PointStruct(
                    id=str(uuid.uuid4()),
                    vector=vector,
                    payload={
                        "path": str(py_file.relative_to(local_path)),
                        "content": content[:15000],
                        "repo": repo_name
                    }
                )]
            )
        except Exception as e:
            logger.error("Failed to index file", file=str(py_file), error=str(e))

    logger.info("Ingestion completed", repo=repo_name)
    return {"status": "completed", "repo": repo_name}