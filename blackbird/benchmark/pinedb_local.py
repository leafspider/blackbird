import time, logging
from pinecone.grpc import PineconeGRPC, GRPCClientConfig
from pinecone import ServerlessSpec
from blackbird.benchmark.generate_embed_fetch import *


vector_dimensions = 384

log = logging.getLogger(__name__)
log.setLevel(logging.INFO)

pc = PineconeGRPC(
    api_key="pclocal", 
    host="http://localhost:5080" 
)   
log.info(
    print("Connected to Pinecone at localhost")
)

def create_index(index_name):

    if not pc.has_index(index_name):

        dense_index_model = pc.create_index(
            name=index_name,
            vector_type="dense",
            dimension=vector_dimensions,
            metric="cosine",
            spec=ServerlessSpec(cloud="aws", region="us-east-1"),
            deletion_protection="disabled",
            tags={"environment": "development"}
        )
        return dense_index_model

def get_index(index_name):

    index_host = pc.describe_index(name=index_name).host
    return pc.Index(host=index_host, grpc_config=GRPCClientConfig(secure=False))

def upsert(index_name, namespace, records):
    
    index = get_index(index_name)
    index.upsert(
        vectors=records,
        namespace=namespace
    )

def query(index_name, namespace, top_k, query_text=None, query_vector=None):

    index = get_index(index_name)
    # index.set_pool_threads(50)
    # index.set_connection_pool_maxsize(50)

    if query_vector is None:
        query_vector = embed(query_text)

    results = index.query(
        namespace=namespace,
        vector=query_vector,
        # filter={"genre": {"$eq": "documentary"}},
        top_k=top_k,
        # include_values=False,
        include_metadata=True,
        # fields=["category", "chunk_text"]
    )

    return results


if __name__ == '__main__':
    
    create_index(index_name)    

    hash = {}

    t0 = time.time()
    # for namespace in namespaces:    
    #     records = fetch_records(topics=namespace['topics'])
    #     hash[namespace['name']] = records
    # print("fetch", time.time() - t0)

    t0 = time.time()
    # for namespace, records in hash.items():    
    #     upsert(index_name, namespace, records)
    # print("upsert", time.time() - t0)
    
    query_vector1 = embed("Which technology will have biggest possible societal impact in the near future?")
    query_vector2 = embed("Which technology will have biggest possible economic impact over the next few years?")

    t0 = time.time()    
    for namespace in namespaces:
        results = query(index_name, namespace=namespace['name'], top_k=1, query_vector=query_vector1)
        results = query(index_name, namespace=namespace['name'], top_k=1, query_vector=query_vector2)
        # print(results)
    print("query", time.time() - t0)