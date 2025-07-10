<!---
Copyright 2025 Leafspider Inc. All rights reserved.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
-->

<h1>Leafspider</h1>
<p align="center">    
    <a href="https://leafspider.com">
        <picture>
            <img src="https://leafspider.com/logo.png" width="60" style="max-width: 100%;">
        </picture>
    </a>    
</p>

<h2 align="center">
    <p>Software and Data Science</p>
</h2>

<h3>Blackbird</h3>

Blackbird provides a benchmark comparison of Pinecone and Pgvector. This is done by using an LLM to generate tweets, which are then indexed and embedded into a local database. Benchmarks are made for upsert and query operations. 

## Installation

Blackbird requires Docker to be installed.

```shell
# pip
pip install docker
```

## Quickstart

Start docker containers for Pgvector, Pinecone, Ollama and Embedder:

```shell
cd blackbird
docker-compose up
```

<details>
<summary>Generate the data</summary>

```py
from blackbird.generate.generator import TweetGenerator


num_tweets = 10

namespaces = [
    {"name": "robotics", "topics": ["Artificial Intelligence", "Robotics"]},
]  

for namespace in namespaces:

    topics = namespace['topics']
    
    gen = TweetGenerator(folder="data_test/tweets")

    for topic in topics:
        dataset = await gen.generate_dataset(topic, num_tweets)

        gen.save_tweets_to_file(dataset, topic)
        tweets = gen.fetch(topic=topic)
        print(tweets)
```

</details>

<details>
<summary>Run the benchmark for local Pgvector</summary>

```py
from blackbird.benchmark.pgvector_local import *


namespaces = [
    {"name": "robotics", "topics": ["Artificial Intelligence", "Robotics"]},
]  

db.create_vector_extension()
for namespace in namespaces:  
    db.create_schema(namespace['name'])
    db.create_table(table=namespace['name']+'.blocks', vector_dimensions=vector_dimensions)
    db.create_unique_index(table=namespace['name']+'.blocks', column='id')

hash = {}

t0 = time.time()
for namespace in namespaces:    
    records = fetch_records_local(topics=namespace['topics'])
    hash[namespace['name']] = records
print("fetch", time.time() - t0)

t0 = time.time()
for namespace, records in hash.items():    
    upsert(namespace, records)
print("upsert", time.time() - t0)

query_vector1 = await embed("Which technology will have biggest possible societal impact in the near future?")
query_vector2 = await embed("Which technology will have biggest possible economic impact over the next few years?")

t0 = time.time()    
for namespace in namespaces:
    results = query(namespace=namespace['name'], top_k=1, query_vector=query_vector1)
    results = query(namespace=namespace['name'], top_k=1, query_vector=query_vector2)
print("query", time.time() - t0)
```

</details>

<details>
<summary>Run the benchmark for local Pinecone</summary>

```py
from blackbird.benchmark.pinecone_local import *


namespaces = [
    {"name": "robotics", "topics": ["Artificial Intelligence", "Robotics"]},
]

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
print("upsert", time.time() - t0)

query_vector1 = await embed("Which technology will have biggest possible societal impact in the near future?")
query_vector2 = await embed("Which technology will have biggest possible economic impact over the next few years?")

t0 = time.time()    
for namespace in namespaces:
    results = query(index_name, namespace=namespace['name'], top_k=1, query_vector=query_vector1)
    results = query(index_name, namespace=namespace['name'], top_k=1, query_vector=query_vector2)
print("query", time.time() - t0)
```

</details>

