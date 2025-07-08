import pytest, asyncio

from typing import List
from blackbird.generate.generator import TweetGenerator
from datetime import datetime

from blackbird.benchmark.namespaces import namespaces_small, namespaces_large

def test_generate_text():

    topics = ["Quantum Computing"]
    
    gen = TweetGenerator(folder="data_test/tweets")

    for topic in topics:
        tweet = gen.generate_text(topic)
        print(tweet)

@pytest.mark.asyncio
async def test_generate_json():
    
    topics = ["Nuclear Fusion"]
    
    gen = TweetGenerator(folder="data_test/tweets")

    for topic in topics:
        tweet = await gen.generate_json(topic, date=datetime.now())
        print(tweet['created_at'])

@pytest.mark.asyncio
async def test_generate_dataset():

    num_tweets = 1

    namespaces = namespaces_small
    # namespaces = namespaces_large
    
    for namespace in namespaces:

        topics = namespace['topics']
        # topics = ["Synthetic Biology"]
        
        gen = TweetGenerator(folder="data_test/tweets")

        for topic in topics:
            dataset = await gen.generate_dataset(topic, num_tweets)
            # print(type(dataset))
            for data in dataset:
                print(type(data))
                print(data)

            gen.save_tweets_to_file(dataset, topic)
            tweets = gen.fetch(topic=topic)
            # print(tweets)

            assert len(tweets) > 0
            assert isinstance(tweets, List)
            assert isinstance(tweets[0]['id'], int)


if __name__ == '__main__':

    asyncio.run(test_generate_dataset())