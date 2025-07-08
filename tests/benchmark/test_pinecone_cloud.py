import pytest
from blackbird.benchmark.pinecone_cloud import *
from blackbird.benchmark.namespaces import namespaces_small, namespaces_large


@pytest.mark.asyncio
async def test_pinecone_cloud():
    
    index_name = "benchmark1"

    namespaces = namespaces_small
    # namespaces = namespaces_large

    create_index(index_name)    

    hash = {}

    t0 = time.time()
    for namespace in namespaces:    
        records = fetch_records_cloud(topics=namespace['topics'])
        hash[namespace['name']] = records
    print("fetch", time.time() - t0)

    t0 = time.time()
    for namespace, records in hash.items():    
        upsert(index_name, namespace, records)
        # upsert(namespace, records)
    print("upsert", time.time() - t0)
    
    query_text1 = "Which technology will have biggest possible societal impact in the near future?"
    query_text2 = "Which technology will have biggest possible economic impact over the next few years?"

    t0 = time.time()    
    for namespace in namespaces:
        results = query(index_name, namespace=namespace['name'], top_k=1, query_text=query_text1)
        results = query(index_name, namespace=namespace['name'], top_k=1, query_text=query_text2)
        # print(results)
    print("query", time.time() - t0)


if __name__ == '__main__':

    asyncio.run(test_pinecone_cloud())
