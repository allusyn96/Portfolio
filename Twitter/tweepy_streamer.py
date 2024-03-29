from tweepy import API
from tweepy import Cursor
from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream
from textblob import TextBlob

import twitter_access
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import re

#Twitter Client
class TwitterClient():
    "A Twitter client"
    def __init__(self, twitter_user=None):
        self.auth = TwitterAuthenticator().authenticate_twitter_app()
        self.twitter_client = API(self.auth)   

        self.twitter_user = twitter_user

    def get_twitter_client_api(self):
        return self.twitter_client

    def get_user_timeline_tweets(self, num_tweets):
        tweets = []
        for tweet in Cursor(self.twitter_client.user_timeline, id=self.twitter_user).items(num_tweets):
            tweets.append(tweet)
        return tweets

    def get_friend_list(self, num_friends):
        friend_list = []
        for friend in Cursor(self.twitter_client.friends, id=self.twitter_user).items(num_friends):
            friend_list.append(friend)
        return friend_list

    def get_home_timeline_tweets(self, num_tweets):
        home_timeline_tweets = []
        for tweet in Cursor(self.twitter_client.home_timeline, id=self.twitter_user).items(num_tweets):
            home_timeline_tweets.append(tweet)
        return home_timeline_tweets

class TwitterAuthenticator():
    """
    Class to authenticate app credentials
    """
    def authenticate_twitter_app(self):
        auth = OAuthHandler(twitter_access.CONSUMER_KEY, twitter_access.CONSUMER_SECRET)
        auth.set_access_token(twitter_access.ACCESS_TOKEN, twitter_access.ACCESS_TOKEN_SECRET)
        return auth

class TwitterStreamer():
    """
    Class for streaming and processing live tweets, posting them to a file
    """
    def __init__(self):
        self.twitter_authenticator = TwitterAuthenticator()

    def stream_tweets(self, fetched_tweets_filename, hash_tag_list):
        # This handles Twitter authentication and the connection to the Twitter Streaming API.
        listener = TwitterListener(fetched_tweets_filename)
        auth = self.twitter_authenticator.authenticate_twitter_app()
        stream = Stream(auth, listener)

        stream.filter(track=hash_tag_list)

class TwitterListener(StreamListener):
    """
    This is a basic listener class that prints tweets to stdout
    """
    def __init__(self, fetched_tweets_filename):
        self.fetched_tweets_filename = fetched_tweets_filename

    def on_data(self, data):
        try:
            print(data)
            with open('tweets.txt', 'w') as f:
                f.write(data)
        except BaseException as e:
            print('Error on data: %s' % str(e))
        return True

    def on_error(self, status):
        if status == 420:
            # Returning false on data method in case of rates limit
            return False
        print(status)

class TweetAnalyzer():
    '''
    Analyzing and categorizing content from tweets
    '''
    def tweets_do_dataframe(self, tweets):
        df = pd.DataFrame(data=[tweet.text for tweet in tweets], columns=['tweets'])

        df['id'] = np.array([tweet.id for tweet in tweets])
        df['len'] = np.array([len(tweet.text) for tweet in tweets])
        df['date'] = np.array([tweet.created_at for tweet in tweets])
        df['source'] = np.array([tweet.source for tweet in tweets])
        df['likes'] = np.array([tweet.favorite_count for tweet in tweets])
        df['retweets'] = np.array([tweet.retweet_count for tweet in tweets])

        return df

    def clean_tweet(self, tweet):
        return ' '.join(re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t])|(\w+:\/\/\S+)", " ", tweet).split())

    def analyze_sentiment(self, tweet):
        cleaned_tweet = self.clean_tweet(tweet)
        analysis = TextBlob(self.clean_tweet(tweet))

        if analysis.sentiment.polarity > 0: return 1 #positive
        elif analysis.sentiment.polarity < 0: return -1 #negative
        else: return 0 #neutral

if __name__ == '__main__':

    '''
    hash_tag_list = ['kylie jenner', 'drake', 'kanye', 'kim kardashian']
    fetched_tweets_filename = 'tweets.json'

    #twitter_streamer = TwitterStreamer()
    #twitter_streamer.stream_tweets(fetched_tweets_filename, hash_tag_list)
    
    twitter_client = TwitterClient('pycon')
    print(twitter_client.get_user_timeline_tweets(1))
    '''


    #Create client to use API
    twitter_client = TwitterClient()
    api = twitter_client.get_twitter_client_api()

    #get tweets from user
    tweets = api.user_timeline(screen_name='realDonaldTrump', count=200)

    #call function to store tweets in a dataframe
    tweet_analyzer = TweetAnalyzer()
    df = tweet_analyzer.tweets_do_dataframe(tweets)
    df['sentiment'] = np.array([tweet_analyzer.analyze_sentiment(tweet) for tweet in df['tweets']])
    print(df.head())

    '''
    #Get average length over all tweets
    #print(np.mean(df['len']))

    #Get max number of likes for a tweet
    #print(np.max(df['likes']))

    #Get max number of retweets for a tweet
    #print(np.max(df['retweets']))

    #Time Series Plot showing the number of likes for tweets over the course of a few dates
    time_likes = pd.Series(data=df['likes'].values, index=df['date'])
    time_likes.plot(figsize=(16, 4), color='r')
    plt.show()

    time_retweets = pd.Series(data=df['retweets'].values, index=df['date'])
    time_retweets.plot(figsize=(16, 4), color='r')
    plt.show()

    time_likes = pd.Series(data=df['likes'].values, index=df['date'])
    time_likes.plot(figsize=(16, 4), label='likes', legend=True)

    time_retweets = pd.Series(data=df['retweets'].values, index=df['date'])
    time_retweets.plot(figsize=(16, 4), label='retweets', legend=True)
    plt.show()
    '''
