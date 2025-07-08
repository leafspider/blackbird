import random, uuid, asyncio, pytest
import psycopg2, psycopg2.extras
from psycopg2.extensions import connection
from blackbird.benchmark.vectordb import VectorDb
import os, logging
from typing import List
from blackbird.generate.embedder import Embedder


log = logging.getLogger(__name__)
log.setLevel(logging.INFO)

psycopg2.extras.register_uuid()

@pytest.mark.asyncio
async def test_embedder_with_local_vector_db():

    db_config = {
        "user": os.environ['POSTGRES_USER'],
        "password": os.environ['POSTGRES_PASSWORD'],
        "host": os.environ['POSTGRES_HOST'],
        "database": os.environ['POSTGRES_DBNAME'],
        "port": os.environ['POSTGRES_PORT'],
    }

    db = VectorDb(db_config)

    db.connect()
    assert isinstance(db.conn, connection)

    text1 = """Question from a trad climbing beginner. What's the methodology for climbing trad routes that have no anchors in areas where slinging trees is prohibited. For example, the climbs Larry and Curly at Old Baldy. Are people building gear anchors at the top of the climb and then cleaning the route, disassembling the anchor, and walking off? If there are no features other than trees on the top of the cliff it seems like disassembling the anchor would be difficult and dangerous, and I cannot imagine doing this. Apologies if I am missing some obvious here."""
    text2 = """Question from a sport beginner. What is the methodology for climbing sport routes that have no anchors in areas where slinging trees is prohibited. For example, the climbs Larry and Curly at Old Baldy. Are people building gear anchors at the top of the climb and then cleaning the route, disassembling the anchor, and walking off? If there are no features other than trees on the top of the pool it seems like eating the anchor would be difficult and dangerous, and I cannot imagine doing this. Apologies if I am an idiot."""
    text3 = """Question from a stock trader. Why are you so interested in horses? I find they cost a lot of money to maintain and are quite smelly. And they eat hay, which is rather delicious."""

    embedder = Embedder()

    vector1 = await embedder.create_embedding(text1)
    assert len(vector1) > 0
    assert isinstance(vector1, List)
    assert isinstance(vector1[0], float)

    vector2 = await embedder.create_embedding(text2)
    assert len(vector2) > 0
    assert isinstance(vector2, List)
    assert isinstance(vector2[0], float)

    vector3 = await embedder.create_embedding(text3)
    assert len(vector3) > 0
    assert isinstance(vector3, List)
    assert isinstance(vector3[0], float)

    doc_id1 = db.insert(
        text=text1, 
        embedding=vector1
    )
    # assert isinstance(doc_id1 , uuid.UUID )
    assert doc_id1 > 0

    doc_id2 = db.insert(
        table='blocks',
        text=text2, 
        embedding=vector2
    )
    # assert isinstance(doc_id2 , uuid.UUID )
    assert doc_id2 > 0

    doc_id3 = db.insert(
        table='blocks',
        text=text3, 
        embedding=vector3
    )
    # assert isinstance(doc_id3 , uuid.UUID )
    assert doc_id3 > 0

    vector1 = db.fetch_embedding(doc_id1)
    assert len(vector1) > 0
    assert isinstance(vector1, List)
    assert isinstance(vector1[0], float)

    rows = db.search_by_embedding(vector1, top_k=3)
    assert len(rows) < 4
    for row in rows:
        # assert isinstance(row[0], uuid.UUID)
        assert isinstance(row[0], int)
        assert isinstance(row[1], str)
        assert isinstance(row[2], float)

    num_results = 100
    rows = db.search_by_id(doc_id1, num_results)
    assert len(rows) < num_results + 1
    for row in rows:
        # assert isinstance(row[0], uuid.UUID)
        assert isinstance(row[0], int)
        assert isinstance(row[1], str)
        assert isinstance(row[2], float)

    for row in rows:
        id = row[0]
        text = db.fetch_text(id)[:50]
        print(text)

    # assert db.delete(doc_id1) == "DELETE 1"
    # assert db.delete(doc_id2) == "DELETE 1"
    # assert db.delete(doc_id3) == "DELETE 1"

    db.disconnect()


@pytest.mark.asyncio
async def test_benchmark_with_local_vector_db():

    db_config = {
        "user": os.environ['POSTGRES_USER'],
        "password": os.environ['POSTGRES_PASSWORD'],
        "host": os.environ['POSTGRES_HOST'],
        "database": os.environ['POSTGRES_DBNAME'],
        "port": os.environ['POSTGRES_PORT'],
    }

    db = VectorDb(db_config)

    db.connect()
    assert isinstance(db.conn, connection)

    # text1 = "Which technology will have biggest possible societal impact in the near future?"
    text1 = "Which technology will have biggest possible economic impact in the near future?"

    print(text1)

    embedder = Embedder()

    vector1 = await embedder.create_embedding(text1)
    assert len(vector1) > 0
    assert isinstance(vector1, List)
    assert isinstance(vector1[0], float)

    rows = db.search_by_embedding(vector1, top_k=5)
    assert len(rows) < 6
    for row in rows:
        assert isinstance(row[0], str)
        assert isinstance(row[1], str)
        assert isinstance(row[2], float)

    for row in rows:
        id = row[0]
        text = db.fetch_text(id)[:]
        print( str(row[2]), text )

    db.disconnect()


if __name__ == '__main__':

    asyncio.run(test_embedder_with_local_vector_db())
    # asyncio.run(test_benchmark_with_local_vector_db())
    

