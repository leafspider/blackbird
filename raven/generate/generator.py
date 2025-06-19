from langchain_ollama import OllamaLLM
from langchain.prompts import PromptTemplate
from datetime import datetime, timedelta
import random
import os, json
from faker import Faker

from raven.generate.embedder import Embedder
import asyncio


class TweetGenerator:

    def __init__(s, folder="data/tweets"):

        s.folder = folder
        os.makedirs(s.folder + "/", exist_ok=True)

        # Initialize the model
        s.llm = OllamaLLM(model="llama3.1", temperature=1.0)  # any local model
        
        # Initialize for generating fake data
        s.fake = Faker()

        s.embedder = Embedder()

        # Create a prompt template for generating tweets
        s.prompt = PromptTemplate(
            input_variables=["topic"],
            template="Generate a tweet about {topic} containing 280 characters or less."
        )        

        # Create a chain
        s.chain = s.prompt | s.llm

    # Generate text
    def generate_text(s, topic):
        return s.clean(s.chain.invoke(topic))
    
    def clean(s, txt):
        return txt[1:len(txt)-1]
    
    # Generate a tweet
    def generate_json(s, topic, date=None):

        # Default to the last week
        if date is None:
            date = s.fake.date_time_between(start_date="-1w", end_date="now")

        # tweet = {
        #     "user": {
        #         "id": s.fake.random_number(digits=10),
        #         "name": s.fake.name(),
        #         "screen_name": s.fake.user_name(),
        #         "location": s.fake.city(),
        #         "followers_count": random.randint(0, 1000000),
        #         "friends_count": random.randint(0, 10000),
        #     },
        #     "id": s.fake.random_number(digits=19),
        #     "created_at": date.isoformat(),            
        #     "text": s.generate_text(topic),                 # "text": s.fake.text(max_nb_chars=280),
        #     "retweet_count": random.randint(0, 10000),
        #     "favorite_count": random.randint(0, 20000),
        #     "lang": random.choice(["en", "es", "fr", "de", "it"]),
        #     "hashtags": [s.fake.word() for _ in range(random.randint(0, 5))],
        #     "mentions": [f"@{s.fake.user_name()}" for _ in range(random.randint(0, 3))],
        # }

        text = s.fake.text(max_nb_chars=280)        # Generate text using Faker
        # text = s.generate_text(topic)             # Generate text using the LLM
        
        tweet = {
            "id": s.fake.random_number(digits=19),
            "created_at": date.isoformat(),            
            "text": text,
            "values": s.embed(text),
        }
        return tweet

    def embed(s, text):
        results = asyncio.run( s.embedder.create_embedding(text) )        # TODO May need to replace with sync version
        return results

    # Generate a list of tweets
    def generate_dataset(s, topic, num_tweets):
        dataset = [s.generate_json(topic) for _ in range(num_tweets)]
        return dataset
    
    # Save to file
    def save_tweets_to_file(s, dataset, topic):   
        with open( s.folder + "/" + topic + ".json", "w") as f:
            json.dump(dataset, f, indent=2)
            print(f"Generated {len(dataset)} tweets and saved to {topic}.json")
    
    # Fetch tweets from file
    def fetch(s, topic):        
        with open( s.folder + "/" + topic + ".json", "r") as f:
            s.df = json.load(f)
        return s.df

    # Get text from fetched tweets
    def get_text(s, topic):
        df = s.fetch(topic)
        doc = ''
        for entry in df:
            text = entry['text']
            doc += text + '\n'
        return doc


if __name__ == "__main__":

    num_tweets = 10

    topics = ["Artificial Intelligence"]
    # topics = ["Space Exploration", "Climate Change"]
    # topics = ["Sustainability", "Renewable Energy"]
    # topics = ["Artificial Intelligence", "Robotics", "Space Exploration", "Climate Change", "Sustainability", "Renewable Energy"]
    # topics = ["Nuclear Fusion", "Quantum Computing", "CRISPR Technology", "Electric Vehicles", "Blockchain Technology"]
    # topics = ["CRISPR Technology", "Synthetic Biology"]
    # topics = ["Artificial Intelligence", "Robotics", "Climate Change","Sustainability", "Renewable Energy", "Nuclear Fusion", 
    #         "Quantum Computing", "Blockchain Technology", "Electric Vehicles", "Space Exploration", "CRISPR Technology", "Synthetic Biology"]
    
    gen = TweetGenerator()

    for topic in topics:

        dataset = gen.generate_dataset(topic, num_tweets)
        gen.save_tweets_to_file(dataset, topic)

        # print(type(dataset))
        # for data in dataset:
        #     print(type(data))
        #     # obj = json.load(data)
        #     # json.dump(obj, indent=2)
        #     print(data)        

