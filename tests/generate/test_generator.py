import pytest, asyncio

from typing import List
from blackbird.generate.generator import TweetGenerator
from datetime import datetime


@pytest.mark.asyncio
async def test_generator():
    
    num_tweets = 3

    topics = ["Synthetic Biology"]
    
    gen = TweetGenerator(folder="data_test/tweets")

    for topic in topics:
        tweet = gen.generate_text(topic)
        print(tweet)

    for topic in topics:
        tweet = await gen.generate_json(topic, date=datetime.now())
        print(tweet['created_at'])

    for topic in topics:
        dataset = await gen.generate_dataset(topic, num_tweets)
        # print(type(dataset))
        for data in dataset:
            print(type(data))
            print(data)

        gen.save_tweets_to_file(dataset, topic)
        tweets = gen.fetch(topic=topic)
        print(tweets)

    # assert len(results) > 0
    # assert isinstance(results, List)
    # assert isinstance(results[0], float)


if __name__ == '__main__':

    asyncio.run(test_generator())