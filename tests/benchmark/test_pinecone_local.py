import pytest
from blackbird.benchmark.pinecone_local import *
from blackbird.benchmark.namespaces import namespaces_small, namespaces_large


@pytest.mark.asyncio
async def test_pinecone_local():
    
    namespaces = namespaces_small
    # namespaces = namespaces_large

    create_index(index_name)    

    hash = {}

    t0 = time.time()
    for namespace in namespaces:    
        records = fetch_records_local(topics=namespace['topics'])
        hash[namespace['name']] = records
    print("fetch", time.time() - t0)

    t0 = time.time()
    for namespace, records in hash.items():    
        upsert(index_name, namespace, records)
        # upsert(namespace, records)
    print("upsert", time.time() - t0)
    
    query_vector1 = await embed("Which technology will have biggest possible societal impact in the near future?")
    query_vector2 = await embed("Which technology will have biggest possible economic impact over the next few years?")

    t0 = time.time()    
    for namespace in namespaces:
        results = query(index_name, namespace=namespace['name'], top_k=1, query_vector=query_vector1)
        results = query(index_name, namespace=namespace['name'], top_k=1, query_vector=query_vector2)
        # print(results)
    print("query", time.time() - t0)


if __name__ == '__main__':

    asyncio.run(test_pinecone_local())