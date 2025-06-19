import random, uuid, asyncio, pytest
import psycopg2, psycopg2.extras
from psycopg2.extensions import connection
from raven.benchmark.vectordb import VectorDb
import os

#pytest_plugins = ("pytest_asyncio",)

import logging
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)

psycopg2.extras.register_uuid()

db_config = {
    "user": os.environ['POSTGRES_USER'],
    "password": os.environ['POSTGRES_PASSWORD'],
    "host": os.environ['POSTGRES_HOST'],
    "database": os.environ['POSTGRES_DBNAME'],
    "port": os.environ['POSTGRES_PORT'],
}


@pytest.mark.asyncio
async def test_create_table():
    
    db = VectorDb(db_config)

    db.connect()
    assert isinstance(db.conn, connection)

    ret = db.create_table()
    assert ret == 'CREATE TABLE'

    # If required
    # db.add_primary_key(table="blocks", column="id")
    # db.create_unique_index(table="blocks", column="content_id")
    # db.add_unique_constraint(table="blocks", column="content_id")

@pytest.mark.asyncio
async def test_create_vector_extension():
    
    db = VectorDb(db_config)

    db.connect()
    assert isinstance(db.conn, connection)

    ret = db.create_vector_extension()
    assert ret == 'CREATE EXTENSION'

@pytest.mark.asyncio
async def test_create_embedding_index():
    
    db = VectorDb(db_config)

    db.connect()
    assert isinstance(db.conn, connection)

    # If required
    # db.add_primary_key(table="blocks", column="id")
    # db.create_unique_index(table="blocks", column="content_id")
    # db.add_unique_constraint(table="blocks", column="content_id")

    # ret = db.create_embedding_index(table="vecs.vecs", column="vec")
    ret = db.create_embedding_index(table="blocks", column="embedding")
    assert ret == 'CREATE INDEX'



@pytest.mark.asyncio
async def test_local_vector_db():
    
    db = VectorDb(db_config)

    db.connect()
    assert isinstance(db.conn, connection)

    # If required
    # db.add_primary_key(table="blocks", column="id")
    # db.create_unique_index(table="blocks", column="content_id")
    # db.add_unique_constraint(table="blocks", column="content_id")

    # ret = db.create_embedding_index(table="blocks", column="embedding")
    # assert ret == 'CREATE INDEX'

    vector1 = [random.random() for _ in range(384)]
    vector1 = [round(x,5) for x in vector1]

    doc_id = db.insert(
        table='blocks',
        block_type='doc',
        parent_id=uuid.UUID('10004654-89ea-44f7-bf32-33ec02d233fa'),
        text='TROUT', 
        embedding=vector1
    )
    assert isinstance(doc_id , uuid.UUID )

    vector2 = [random.random() for _ in range(384)]
    vector2 = [round(x,5) for x in vector2]

    updated = db.update(doc_id, table='blocks', text="GREAT CONTENT")
    assert updated == "UPDATE 1"

    fake_block_id = uuid.UUID('55004654-89ea-44f7-bf32-22ec02d233fa')
    updated = db.update(fake_block_id, table='blocks', text="BOGUS CONTENT")
    assert updated == "UPDATE 0"

    updated = db.update(
        doc_id,
        table='blocks',
        block_type='doc',
        parent_id=uuid.UUID('10004654-89ea-44f7-bf32-33ec02d233fa'),
        text='A TSUNAMI of fantastic content', 
        embedding=vector2
    )
    assert updated == "UPDATE 1"

    vector3 = db.fetch_embedding(doc_id)
    assert vector3 == vector2

    rows = db.search_by_embedding(vector3, num_results=3)
    assert len(rows) < 4
    for row in rows:
        assert isinstance(row[0], uuid.UUID)
        assert isinstance(row[1], float)

    rows = db.search_by_id(doc_id, num_results=4)
    assert len(rows) < 5
    for row in rows:
        assert isinstance(row[0], uuid.UUID)
        assert isinstance(row[1], float)

    data = {}
    rows = db.search_by_id(doc_id, num_results=10)
    for row in rows:
        id = row[0]
        # text = db.fetch_text(id)[:100]
        val = db.select(id, db.table, {'id', db.text_column})
        #print(val)            
        data['id'] = val[0][1]
        data[db.text_column] = val[0][0]

    print(data)
    
    deleted = db.delete(doc_id)
    assert deleted == "DELETE 1"
    deleted = db.delete(doc_id)
    assert deleted == "DELETE 0"

    db.disconnect()


@pytest.mark.asyncio
async def test_insert():
    
    db = VectorDb(db_config)
    db.connect()
    assert isinstance(db.conn, connection)
    vector1 = [random.random() for _ in range(384)]
    doc_id = db.insert(
        table='blocks',
        text='TROUT', 
        embedding=vector1
    )
    assert isinstance(doc_id , int )
    db.disconnect()

@pytest.mark.asyncio
async def test_upsert():
    
    db = VectorDb(db_config)
    db.connect()
    assert isinstance(db.conn, connection)
    
    keys = ['id', 'text', 'embedding']
    values=[(str(x), 'PERCH'+str(x), str([round(random.random(),5) for _ in range(384)])) for x in range(30)]

    ret = db.upsert(
        table='blocks',
        keys=keys,
        values=values
    )
    assert ret == "INSERT 0 30"

    db.disconnect()


if __name__ == '__main__':

    # asyncio.run(test_cloud_vector_search())
    # asyncio.run(test_local_vector_db())
    # asyncio.run(test_create_embedding_index())
    # asyncio.run(test_create_vector_extension())
    # asyncio.run(test_create_table())
    asyncio.run(test_upsert())
    

