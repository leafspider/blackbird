from langchain_ollama import OllamaLLM
from langchain.prompts import PromptTemplate
from datetime import datetime, timedelta
import random
import os, json
from faker import Faker

from blackbird.generate.embedder import Embedder
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
    async def generate_json(s, topic, date=None):

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

        # text = s.fake.text(max_nb_chars=280)        # Generate text using Faker
        text = s.generate_text(topic)             # Generate text using the LLM
        
        tweet = {
            "id": s.fake.random_number(digits=19),
            "created_at": date.isoformat(),            
            "text": text,
            "values": await s.embed(text),
        }
        return tweet

    async def embed(s, text):
        # results = asyncio.run( s.embedder.create_embedding(text) )        # TODO May need to replace with sync version
        return await s.embedder.create_embedding(text)

    # Generate a list of tweets
    async def generate_dataset(s, topic, num_tweets):
        tasks = [s.generate_json(topic) for _ in range(num_tweets)]             # concurrent
        return await asyncio.gather(*tasks)       
         
        # dataset = [await s.generate_json(topic) for _ in range(num_tweets)]   # sequential
        # return dataset    
    
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

    from tests.generate.test_generator import test_generate_dataset

    asyncio.run(test_generate_dataset())

