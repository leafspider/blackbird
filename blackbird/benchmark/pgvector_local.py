import os, time, asyncio
from blackbird.benchmark.vectordb import VectorDb
from blackbird.benchmark.generate_embed_fetch import *


vector_dimensions = 384

db_config = {
    "user": os.environ['POSTGRES_USER'],
    "password": os.environ['POSTGRES_PASSWORD'],
    "host": os.environ['POSTGRES_HOST'],
    "database": os.environ['POSTGRES_DBNAME'],
    "port": os.environ['POSTGRES_PORT'],
}

db = VectorDb(db_config)
db.connect()

def upsert(namespace, records):
    
    keys = ['id', 'text', 'embedding']
    values=[(record['id'], record['metadata']['chunk_text'], str(record['values'])) for record in records]
    ret = db.upsert(
        table=namespace+'.blocks',
        keys=keys,
        values=values
    )
    return ret

def query(index_name, namespace, top_k, query_text=None, query_vector=None):

    if query_vector is None:
        query_vector = embed(query_text)
    return db.search_by_embedding(query_vector, table=namespace+'.blocks', top_k=top_k)


if __name__ == '__main__':
    
    db.create_vector_extension()
    for namespace in namespaces:  
        db.create_schema(namespace['name'])
        db.create_table(table=namespace['name']+'.blocks', vector_dimensions=vector_dimensions)
        db.create_unique_index(table=namespace['name']+'.blocks', column='id')

    hash = {}

    t0 = time.time()
    for namespace in namespaces:    
        records = fetch_records(topics=namespace['topics'])
        hash[namespace['name']] = records
    print("fetch", time.time() - t0)

    t0 = time.time()
    for namespace, records in hash.items():    
        upsert(namespace, records)
    print("upsert", time.time() - t0)
    
    query_vector1 = embed("Which technology will have biggest possible societal impact in the near future?")
    query_vector2 = embed("Which technology will have biggest possible economic impact over the next few years?")

    t0 = time.time()    
    for namespace in namespaces:
        results = query(index_name, namespace=namespace['name'], top_k=1, query_vector=query_vector1)
        results = query(index_name, namespace=namespace['name'], top_k=1, query_vector=query_vector2)
        # print(results)
    print("query", time.time() - t0)




