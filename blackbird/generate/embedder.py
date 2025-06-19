import asyncio, logging, os
from typing import Any, List
from aiohttp import ClientSession, BasicAuth


log = logging.getLogger("Embedder")
log.setLevel(logging.DEBUG)

class Embedder:

    def __init__(self):

        self.url = f"{os.environ['EMBEDDING_PROTOCOL']}://{os.environ['EMBEDDING_HOST']}:{os.environ['EMBEDDING_PORT']}/embed"
        # self.url = f"{os.environ['EMBEDDING_PROTOCOL']}://{os.environ['EMBEDDING_HOST']}:{os.environ['EMBEDDING_PORT']}/api/embeddings"
        self.auth = BasicAuth(
            login=os.environ['EMBEDDING_USER'], password=os.environ['EMBEDDING_PASSWORD']
        )

    async def create_embedding(self, text: str) -> List[float]:

        async with ClientSession() as session:
            response = await session.post(
                self.url, auth=self.auth, json={"inputs": text}
                # self.url, auth=self.auth, json={"model": "nomic-embed-text", "prompt": text }
            )
            results = await response.json()
        results = results[0]
        log.debug(f"Created embedding with dimension {len(results)}.")

        return results


if __name__ == "__main__":

    from tests.generate.test_embedder import test_embedder

    asyncio.run(test_embedder())
