from blackbird.benchmark.generate_embed_fetch import *
import os, time
from pinecone import Pinecone


pc = Pinecone(
    api_key=os.environ['PINECONE_API_KEY'],
)

def create_index(index_name):

    if not pc.has_index(index_name):

        pc.create_index_for_model(
            name=index_name,
            cloud="aws",
            region="us-east-1",
            embed={
                "model":"llama-text-embed-v2",
                "field_map":{"text": "chunk_text"}
            }
        )

def upsert(index_name, namespace, records):
    
    index = pc.Index(name=index_name)
    index.upsert_records(
        namespace,
        records
    )

def query(index_name, namespace, top_k, query_text=None):
# def query(index_name, namespace, top_k, query_text):

    # if query_vector is None:
    #     query_vector = embed(query_text)

    index = pc.Index(                       # TODO Target by HOST in Production
        name=index_name,
        pool_threads=50,           
        connection_pool_maxsize=50,
    )    
    results = index.search(
        namespace=namespace, 
        query={
            "inputs": {"text": query_text}, 
            "top_k": top_k
        },
        fields=["category", "chunk_text"]
    )

    return results


if __name__ == '__main__':
    
    index_name = "benchmark1"
    namespaces = [
        {"name": "AI and Robotics", "topics": ["Artificial Intelligence", "Robotics"]},
        # {"name": "Climate Change", "topics": ["Climate Change","Sustainability"]},
        # {"name": "Energy", "topics": ["Renewable Energy", "Nuclear Fusion"]},
        # {"name": "Quantum and Blockchain", "topics": ["Quantum Computing", "Blockchain Technology"]},
        # {"name": "Transport", "topics": ["Electric Vehicles", "Space Exploration"]},
        # {"name": "Biotech", "topics": ["CRISPR Technology", "Synthetic Biology"]},
    ]

    create_index(index_name)    

    t0 = time.time()
    for namespace in namespaces:    
        records = fetch_records_cloud( topics=namespace['topics'])    
        upsert(index_name, namespace['name'], records)
    print("upsert", time.time() - t0)
    
    t0 = time.time()    
    for namespace in namespaces:
        results = query(index_name, namespace['name'], top_k=5, query_text="Which technology will have biggest possible societal impact in the near future?")
    print("query", time.time() - t0)
