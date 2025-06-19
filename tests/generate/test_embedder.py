import pytest, asyncio

from typing import List
from raven.generate.embedder import Embedder


@pytest.mark.asyncio
async def test_embedder():
    
    text = "Trout is a wonderfully flavoured fish when it's on your plate. However, when it's in the river it's a voracious predator."
    
    embedder = Embedder()
    
    results = await embedder.create_embedding(text)

    assert len(results) > 0
    assert isinstance(results, List)
    assert isinstance(results[0], float)

    print(results)


if __name__ == '__main__':

    asyncio.run(test_embedder())