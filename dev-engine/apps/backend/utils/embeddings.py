from openai import AsyncOpenAI
from ..core.config import settings

client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

async def get_embedding(text: str) -> list[float]:
    resp = await client.embeddings.create(model="text-embedding-3-small", input=text[:8000])
    return resp.data[0].embedding