from blackbird.generate.generator import TweetGenerator
from blackbird.generate.embedder import Embedder
import asyncio, time


index_name = "benchmark2"
namespaces = [
    {"name": "robotics", "topics": ["Artificial Intelligence", "Robotics"]},
    {"name": "climate", "topics": ["Climate Change","Sustainability"]},
    {"name": "energy", "topics": ["Renewable Energy", "Nuclear Fusion"]},
    {"name": "quantum", "topics": ["Quantum Computing", "Blockchain Technology"]},
    {"name": "transport", "topics": ["Electric Vehicles", "Space Exploration"]},
    {"name": "biotech", "topics": ["CRISPR Technology", "Synthetic Biology"]},
    {"name": "sport", "topics": ["Football", "Basketball"]},
    {"name": "finance", "topics": ["Stock Market", "Cryptocurrency"]},
    {"name": "health", "topics": ["Mental Health", "Physical Fitness"]},
    {"name": "education", "topics": ["Online Learning", "STEM Education"]},
    {"name": "culture", "topics": ["Art and Design", "Music and Entertainment"]},
    {"name": "travel", "topics": ["Adventure Travel", "Cultural Tourism"]},
    {"name": "food", "topics": ["Culinary Arts", "Food Sustainability"]},
    {"name": "history", "topics": ["Ancient Civilizations", "Modern History"]},
    {"name": "psychology", "topics": ["Cognitive Psychology", "Behavioral Psychology"]},
    {"name": "philosophy", "topics": ["Ethics", "Existentialism"]},
    {"name": "sociology", "topics": ["Social Justice", "Urban Studies"]},
    {"name": "politics", "topics": ["International Relations", "Political Theory"]},
    {"name": "law", "topics": ["Criminal Law", "Constitutional Law"]},
    {"name": "environment", "topics": ["Conservation", "Environmental Policy"]},
    {"name": "technology", "topics": ["Cybersecurity", "Data Science"]},
    {"name": "gaming", "topics": ["Video Games", "Game Development"]},
    {"name": "literature", "topics": ["Fiction Writing", "Poetry"]},
    {"name": "marketing", "topics": ["Digital Marketing", "Brand Strategy"]},
    {"name": "entrepreneurship", "topics": ["Startup Culture", "Business Innovation"]},
]   

async def embed(text):

    embedder = Embedder()
    results = await embedder.create_embedding(text)
    return results

def fetch_records_local(topics):

    gen = TweetGenerator()

    records = []
    for topic in topics:
        tweets = gen.fetch(topic=topic)
        for tweet in tweets:
            record = {
                "id": str( tweet['id'] ),
                # "values": embed(tweet['text']),
                "values": tweet['values'],
                "metadata": {
                    "chunk_text": tweet['text'],
                    "category": topic, 
                }
            }
            records.append(record)
    return records

def fetch_records_cloud(topics):

    gen = TweetGenerator()

    records = []
    for topic in topics:
        tweets = gen.fetch(topic=topic)
        for tweet in tweets:
            record = {
                "_id": str( tweet['id'] ),
                "chunk_text": tweet['text'],
                "category": topic, 
            }
            records.append(record)
    return records

async def generate_data(num_tweets):
    
    gen = TweetGenerator()

    t0 = time.time()
    for namespace in namespaces:
        for topic in namespace['topics']:
            dataset = await gen.generate_dataset(topic, num_tweets)
            gen.save_tweets_to_file(dataset, topic)
    print("generate", time.time() - t0)

            
if __name__ == "__main__":

    num_tweets = 2

    asyncio.run( generate_data(num_tweets) )
